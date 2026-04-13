#!/usr/bin/env python3
"""
Conformance Runner — execute test vectors against FLUX Python runtime.

Reads vectors from flux-conformance repo, runs each through the Python VM,
and reports pass/fail with detailed diagnostics.
"""
import json
import sys
import os
from pathlib import Path

# Add flux-runtime to path
FLUX_RUNTIME = os.path.expanduser("~/.openclaw/workspace/repos/flux-runtime")
sys.path.insert(0, f"{FLUX_RUNTIME}/src")

VECTOR_DIR = Path("/tmp/flux-conf/vectors/vectors")

def load_vectors():
    """Load all test vectors from JSON files."""
    vectors = []
    for f in sorted(VECTOR_DIR.glob("*.json")):
        if f.name == "manifest.json":
            continue
        try:
            data = json.loads(f.read_text())
            if isinstance(data, list):
                vectors.extend(data)
            elif isinstance(data, dict) and ("bytecode" in data or "bytecode_hex" in data):
                vectors.append(data)
            elif isinstance(data, dict) and "vectors" in data:
                vectors.extend(data["vectors"])
        except Exception as e:
            print(f"  ⚠️ Error loading {f.name}: {e}")
    return vectors


def parse_bytecode(hex_str):
    """Parse hex bytecode string to bytes."""
    if isinstance(hex_str, list):
        return bytes(hex_str)
    # Handle space-separated hex
    hex_clean = hex_str.replace(" ", "").replace("0x", "")
    return bytes.fromhex(hex_clean)


def run_vector(vector):
    """Execute a single test vector against the Python VM."""
    name = vector.get("name", "unnamed")
    bytecode_hex = vector.get("bytecode_hex", vector.get("bytecode", ""))
    expected = vector.get("expected", {})

    if not bytecode_hex:
        return {"name": name, "status": "SKIP", "reason": "no bytecode"}

    try:
        bytecode = parse_bytecode(bytecode_hex)
    except Exception as e:
        return {"name": name, "status": "ERROR", "reason": f"bytecode parse: {e}"}

    try:
        from flux.vm.interpreter import Interpreter
        
        vm = Interpreter(bytecode)
        cycles = vm.execute()

        actual = {
            "halted": vm.halted,
            "cycles": cycles,
        }

        # Check registers
        expected_regs = {}
        gp = expected.get("gp", {})
        for idx_str, val in gp.items():
            expected_regs[f"R{idx_str}"] = val
        if not expected_regs:
            for key in ["R0", "R1", "R2", "R3", "R4", "R5", "R6", "R7"]:
                if key in expected:
                    expected_regs[key] = expected[key]

        reg_mismatches = []
        for reg, expected_val in expected_regs.items():
            if reg.startswith("R"):
                idx = int(reg[1:])
                try:
                    actual_val = vm.regs.read_gp(idx)
                except:
                    actual_val = None
                if actual_val != expected_val:
                    reg_mismatches.append(f"{reg}: expected {expected_val}, got {actual_val}")

        # Check final state
        expected_state = expected.get("final_state", "HALTED")
        state_ok = True
        if expected_state == "HALTED" and not actual["halted"]:
            state_ok = False

        if reg_mismatches:
            return {
                "name": name,
                "status": "FAIL",
                "reason": f"register mismatch: {'; '.join(reg_mismatches)}",
                "cycles": cycles
            }
        
        if not state_ok:
            return {
                "name": name,
                "status": "FAIL",
                "reason": f"state: expected {expected_state}, not halted after {cycles} cycles",
                "cycles": cycles
            }

        return {"name": name, "status": "PASS", "cycles": cycles}

    except Exception as e:
        return {"name": name, "status": "ERROR", "reason": str(e)[:100]}


def main():
    print("═══ FLUX Conformance Runner (Python) ═══")
    print(f"Vector dir: {VECTOR_DIR}")
    print()

    vectors = load_vectors()
    print(f"Loaded {len(vectors)} test vectors")
    print()

    results = {"PASS": 0, "FAIL": 0, "ERROR": 0, "SKIP": 0}
    fails = []

    for i, v in enumerate(vectors):
        result = run_vector(v)
        results[result["status"]] += 1
        status_icon = {"PASS": "✅", "FAIL": "❌", "ERROR": "⚠️", "SKIP": "⏭️"}
        icon = status_icon.get(result["status"], "?")
        name = result["name"]
        
        if result["status"] in ("FAIL", "ERROR"):
            reason = result.get("reason", "")
            print(f"  {icon} [{i+1}/{len(vectors)}] {name}: {reason}")
            fails.append(result)
        else:
            print(f"  {icon} [{i+1}/{len(vectors)}] {name} ({result.get('cycles', '?')} cycles)")

    print()
    print(f"═══ Results ═══")
    total = sum(results.values())
    for status, count in results.items():
        pct = count / total * 100 if total else 0
        print(f"  {status}: {count}/{total} ({pct:.0f}%)")

    if fails:
        print(f"\n  ❌ {len(fails)} failures:")
        for f in fails[:10]:
            print(f"     {f['name']}: {f.get('reason', '?')}")

    return 0 if results["FAIL"] == 0 and results["ERROR"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
