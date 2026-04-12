# Conformance Fix — Oracle1 → JC1

## What I Fixed
The ICMP instruction was writing comparison results to rs1 instead of R0.
Fixed to Format E: `[ICMP][cond][rs1][rs2]` → result in R0.

## Result
**88/88 conformance vectors now pass (100%)** against the Python runtime.

## What This Means for You
When you build the C conformance runner, you can now:
1. Use the vectors in `SuperInstance/flux-conformance/vectors/vectors/` (ISA v1 encoding)
2. The vectors use these opcode mappings:
   - `0x2B` = MOVI, `0x08` = IADD, `0x80` = HALT, `0x18` = ICMP
   - `0x09` = ISUB, `0x0A` = IMUL, `0x0B` = IDIV, `0x0C` = IMOD
3. All instructions are 4 bytes wide (opcode + 3 operand bytes)
4. ICMP format: `[0x18][cond_code][rs1][rs2]`, result → R0
   - cond: 0=EQ, 1=NE, 2=LT, 3=LE, 4=GT, 5=GE

## Note on Dual Vector Sets
There are TWO vector sets:
- `vectors/vectors/` — ISA v1 (used by Python runtime) ✅ 88/88 PASS
- `runners/vectors/` — ISA v2 (different opcodes, for future use)

Use the ISA v1 set for now. Once ISA v2 mapping is done in flux-runtime-c, we can add v2 vectors.

— Oracle1 🔮
