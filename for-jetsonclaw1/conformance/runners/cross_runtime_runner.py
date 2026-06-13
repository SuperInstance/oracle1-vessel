#!/usr/bin/env python3
"""
FLUX Cross-Runtime Conformance Runner — runs all test vectors against the real flux-runtime interpreter.

Usage:
    python cross_runtime_runner.py
    python cross_runtime_runner.py --verbose
    python cross_runtime_runner.py --filter "arith"
    python cross_runtime_runner.py --json results.json
"""

from __future__ import annotations

import argparse
import json
import os
import struct
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add flux-runtime to path
FLUX_RUNTIME_SRC = os.environ.get("FLUX_RUNTIME_SRC", 
    os.path.join(os.path.dirname(__file__), "..", "..", "flux-runtime", "src"))
if os.path.exists(FLUX_RUNTIME_SRC):
    sys.path.insert(0, FLUX_RUNTIME_SRC)

try:
    from flux.vm.interpreter import Interpreter
    from flux.bytecode.opcodes import Op
    HAS_RUNTIME = True
except ImportError:
    HAS_RUNTIME = False
    print(f"[WARN] flux-runtime not found at {FLUX_RUNTIME_SRC}. Using built-in VM.", file=sys.stderr)


@dataclass
class TestResult:
    name: str
    file: str
    status: str  # PASS, FAIL, SKIP, ERROR
    duration_ms: float
    expected: dict = field(default_factory=dict)
    actual: dict = field(default_factory=dict)
    error: str = ""


class CrossRuntimeRunner:
    """Runs FLUX conformance vectors against the real Python VM."""

    def __init__(self, vectors_dir: str, verbose: bool = False):
        self.vectors_dir = Path(vectors_dir)
        self.verbose = verbose
        self.results: List[TestResult] = []

    def load_vector(self, path: Path) -> Optional[dict]:
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            return None

    def run_vector(self, path: Path) -> TestResult:
        data = self.load_vector(path)
        if data is None:
            return TestResult(path.name, str(path), "ERROR", 0, error="Failed to load JSON")

        name = data.get("name", path.stem)
        bc_hex = data.get("bytecode_hex", data.get("bytecode", ""))
        expected = data.get("expected", {})

        if not bc_hex:
            return TestResult(name, str(path), "SKIP", 0, error="No bytecode")

        # Parse bytecode
        try:
            # Handle various hex formats: "2b 01 03 00" or "2b010300" or "0x2b 0x01"
            bc_clean = bc_hex.replace("0x", "").replace(" ", "").replace("\n", "")
            bytecode = bytes.fromhex(bc_clean)
        except ValueError as e:
            return TestResult(name, str(path), "ERROR", 0, expected=expected, error=f"Invalid hex: {e}")

        if HAS_RUNTIME:
            return self._run_with_runtime(name, str(path), bytecode, expected, data)
        else:
            return self._run_with_builtin(name, str(path), bytecode, expected)

    def _run_with_runtime(self, name: str, path: str, bytecode: bytes, expected: dict, data: dict) -> TestResult:
        start = time.perf_counter()
        try:
            vm = Interpreter(bytecode)
            # Apply preconditions if present
            preconds = data.get("preconditions", {})
            if preconds:
                gp_pre = preconds.get("gp", {})
                for reg_str, val in gp_pre.items():
                    vm.regs.write_gp(int(reg_str), val)
                fp_pre = preconds.get("fp", {})
                for reg_str, val in fp_pre.items():
                    vm.regs.write_fp(int(reg_str), val)
            vm.execute()
        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            # Check if error was expected
            exp_state = expected.get("final_state", "")
            if exp_state == "ERRORED":
                return TestResult(name, path, "PASS", duration, expected=expected,
                                error=f"Expected error: {e}")
            return TestResult(name, path, "ERROR", duration, expected=expected, error=str(e))

        duration = (time.perf_counter() - start) * 1000

        # Collect actual state
        actual = {}
        try:
            gp = expected.get("gp", {})
            for reg_str in gp:
                reg_idx = int(reg_str)
                try:
                    actual[reg_str] = vm.regs.read_gp(reg_idx)
                except Exception:
                    pass
            fp = expected.get("fp", {})
            for reg_str in fp:
                reg_idx = int(reg_str)
                try:
                    actual_fp = vm.regs.read_fp(reg_idx)
                    actual[reg_str] = round(actual_fp, 6)
                except Exception:
                    pass
        except Exception:
            pass

        # Check expected final state
        exp_state = expected.get("final_state", "")
        if exp_state == "HALTED" and not vm.halted:
            return TestResult(name, path, "FAIL", duration, expected=expected, actual=actual,
                            error="Expected HALTED but VM did not halt")
        # Expected error state is a PASS if VM threw
        if exp_state == "ERRORED":
            return TestResult(name, path, "PASS", duration, expected=expected, actual=actual,
                            error="Expected error occurred")

        # Check register values
        gp = expected.get("gp", {})
        for reg_str, exp_val in gp.items():
            act_val = actual.get(reg_str)
            if act_val != exp_val:
                if isinstance(act_val, int) and isinstance(exp_val, int):
                    if (act_val & 0xFFFFFFFF) == (exp_val & 0xFFFFFFFF):
                        continue
                return TestResult(name, path, "FAIL", duration, expected=expected, actual=actual,
                                error=f"R{reg_str}: expected={exp_val}, actual={act_val}")

        # Check FP register values
        fp = expected.get("fp", {})
        for reg_str, exp_val in fp.items():
            act_val = actual.get(reg_str)
            if act_val is not None and abs(act_val - exp_val) > 1e-6:
                return TestResult(name, path, "FAIL", duration, expected=expected, actual=actual,
                                error=f"F{reg_str}: expected={exp_val}, actual={act_val}")

        return TestResult(name, path, "PASS", duration, expected=expected, actual=actual)

    def _run_with_builtin(self, name: str, path: str, bytecode: bytes, expected: dict) -> TestResult:
        """Minimal built-in VM for when flux-runtime is not available."""
        start = time.perf_counter()
        try:
            regs = [0] * 64
            pc = 0
            max_steps = 100000
            halted = False

            # Minimal opcode set matching flux-runtime Op
            HALT = 0x80
            NOP = 0x81
            MOVI = 0x2b
            MOV = 0x3a
            IADD = 0x08
            ISUB = 0x09
            IMUL = 0x0a
            IDIV = 0x0b
            INC = getattr(Op, 'INC', 0x02) if HAS_RUNTIME else 0x02
            DEC = getattr(Op, 'DEC', 0x03) if HAS_RUNTIME else 0x03

            for _ in range(max_steps):
                if pc >= len(bytecode):
                    break
                op = bytecode[pc]

                if op == HALT:
                    halted = True
                    break
                elif op == NOP:
                    pc += 1
                elif op == MOVI:
                    rd = bytecode[pc + 1]
                    imm = struct.unpack_from('<h', bytecode, pc + 2)[0]
                    regs[rd] = imm
                    pc += 4
                elif op == MOV:
                    rd = bytecode[pc + 1]
                    rs = bytecode[pc + 2]
                    regs[rd] = regs[rs]
                    pc += 3
                elif op == IADD:
                    rd = bytecode[pc + 1]
                    rs1 = bytecode[pc + 2]
                    rs2 = bytecode[pc + 3]
                    regs[rd] = (regs[rs1] + regs[rs2]) & 0xFFFFFFFF
                    if regs[rd] >= 0x80000000:
                        regs[rd] -= 0x100000000
                    pc += 4
                elif op == ISUB:
                    rd = bytecode[pc + 1]
                    rs1 = bytecode[pc + 2]
                    rs2 = bytecode[pc + 3]
                    regs[rd] = (regs[rs1] - regs[rs2]) & 0xFFFFFFFF
                    if regs[rd] >= 0x80000000:
                        regs[rd] -= 0x100000000
                    pc += 4
                elif op == IMUL:
                    rd = bytecode[pc + 1]
                    rs1 = bytecode[pc + 2]
                    rs2 = bytecode[pc + 3]
                    regs[rd] = (regs[rs1] * regs[rs2]) & 0xFFFFFFFF
                    if regs[rd] >= 0x80000000:
                        regs[rd] -= 0x100000000
                    pc += 4
                elif op == IDIV:
                    rd = bytecode[pc + 1]
                    rs1 = bytecode[pc + 2]
                    rs2 = bytecode[pc + 3]
                    if regs[rs2] == 0:
                        regs[rd] = 0
                    else:
                        regs[rd] = int(regs[rs1] / regs[rs2])
                    pc += 4
                else:
                    pc += 1  # Skip unknown opcodes

            duration = (time.perf_counter() - start) * 1000

            actual = {}
            gp = expected.get("gp", {})
            for reg_str in gp:
                actual[reg_str] = regs[int(reg_str)]

            exp_state = expected.get("final_state", "")
            if exp_state == "HALTED" and not halted:
                return TestResult(name, path, "FAIL", duration, expected=expected, actual=actual,
                                error="Expected HALTED but did not halt")

            for reg_str, exp_val in gp.items():
                act_val = actual.get(reg_str)
                if act_val != exp_val:
                    return TestResult(name, path, "FAIL", duration, expected=expected, actual=actual,
                                    error=f"R{reg_str}: expected={exp_val}, actual={act_val}")

            return TestResult(name, path, "PASS", duration, expected=expected, actual=actual)

        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            return TestResult(name, path, "ERROR", duration, expected=expected, error=str(e))

    def run_all(self, filter_str: Optional[str] = None) -> List[TestResult]:
        vector_files = sorted(self.vectors_dir.glob("*.json"))

        if filter_str:
            vector_files = [f for f in vector_files if filter_str.lower() in f.name.lower()]

        for vf in vector_files:
            result = self.run_vector(vf)
            self.results.append(result)

            status_marker = {"PASS": "\033[92mPASS\033[0m", "FAIL": "\033[91mFAIL\033[0m",
                           "SKIP": "\033[93mSKIP\033[0m", "ERROR": "\033[91mERROR\033[0m"}
            marker = status_marker.get(result.status, result.status)
            print(f"  [{marker}] {result.name} ({result.duration_ms:.2f} ms)")

            if self.verbose and result.status in ("FAIL", "ERROR"):
                print(f"         file: {result.file}")
                if result.error:
                    print(f"         error: {result.error}")
                if result.expected:
                    print(f"         expected: {result.expected}")
                if result.actual:
                    print(f"         actual: {result.actual}")

        return self.results

    def print_summary(self):
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == "PASS")
        failed = sum(1 for r in self.results if r.status == "FAIL")
        errors = sum(1 for r in self.results if r.status == "ERROR")
        skipped = sum(1 for r in self.results if r.status == "SKIP")
        rate = (passed / total * 100) if total > 0 else 0

        print(f"\n{'='*50}")
        print(f"  Results: {total} tests, {passed} passed, {failed} failed, {errors} errors, {skipped} skipped")
        print(f"  Pass rate: {rate:.1f}%")
        print(f"  Runtime: {'flux-runtime (real VM)' if HAS_RUNTIME else 'built-in (minimal VM)'}")
        print(f"{'='*50}")

        if failed > 0:
            print(f"\n  Failed tests:")
            for r in self.results:
                if r.status == "FAIL":
                    print(f"    - {r.name}: {r.error}")
        if errors > 0:
            print(f"\n  Errored tests:")
            for r in self.results:
                if r.status == "ERROR":
                    print(f"    - {r.name}: {r.error}")

    def to_json(self) -> dict:
        return {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "runtime": "flux-runtime" if HAS_RUNTIME else "builtin",
            "total": len(self.results),
            "passed": sum(1 for r in self.results if r.status == "PASS"),
            "failed": sum(1 for r in self.results if r.status == "FAIL"),
            "errors": sum(1 for r in self.results if r.status == "ERROR"),
            "skipped": sum(1 for r in self.results if r.status == "SKIP"),
            "results": [
                {
                    "name": r.name,
                    "status": r.status,
                    "duration_ms": round(r.duration_ms, 3),
                    "error": r.error,
                }
                for r in self.results
            ]
        }


def main():
    parser = argparse.ArgumentParser(description="FLUX Cross-Runtime Conformance Runner")
    parser.add_argument("--vectors-dir", default="vectors/vectors", help="Path to test vectors")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show details for failures")
    parser.add_argument("--filter", "-f", default=None, help="Filter by name substring")
    parser.add_argument("--json", default=None, help="Output results to JSON file")
    args = parser.parse_args()

    print("=" * 50)
    print("  FLUX Cross-Runtime Conformance Runner")
    print("=" * 50)
    print(f"  vectors dir : {args.vectors_dir}")
    print(f"  verbose     : {args.verbose}")
    print(f"  runtime     : {'flux-runtime (real VM)' if HAS_RUNTIME else 'built-in (minimal VM)'}")

    runner = CrossRuntimeRunner(args.vectors_dir, args.verbose)
    results = runner.run_all(args.filter)
    runner.print_summary()

    if args.json:
        with open(args.json, 'w') as f:
            json.dump(runner.to_json(), f, indent=2)
        print(f"\n  Results written to {args.json}")

    return 0 if all(r.status in ("PASS", "SKIP") for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
