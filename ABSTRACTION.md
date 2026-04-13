primary_plane: 4
reads_from: [3, 4, 5]
writes_to: [3, 4]
floor: 3
ceiling: 5
compilers:
  - name: deepseek-chat
    from: 4
    to: 2
    locks: 7
reasoning: |
  Oracle1-vessel is the Lighthouse coordination agent operating at Plane 4.
  It coordinates fleet activities using Domain Language (4) commands, reading from
  natural Intent (5), Domain Language (4), or Structured IR (3) inputs, and writing
  outputs in both Domain Language (4) for fleet-wide coordination and Structured
  IR (3) for API calls to fleet-agent-api.

  Floor at 3 means oracle1-vessel can interface directly with the structured API
  layer for precise control, but primarily operates at Domain Language for human-
  readable fleet commands. The compiler to Bytecode (2) enables generating
  coordination patterns that flux-runtime can execute as autonomous procedures.
