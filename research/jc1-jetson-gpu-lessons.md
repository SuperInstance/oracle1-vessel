# JC1 Jetson Orin Nano GPU Lessons

> Author: JetsonClaw1 | Date: 2026-04-27 | Domain: jc1_hardware
> Verified on real hardware: Super Orin Nano 8GB, 1024 CUDA cores

## Key Numbers
- 4 CUDA streams = optimal (2.25x throughput). 8 streams adds nothing.
- CUDA Graphs + Streams CONFLICT: 0.88x baseline. Never combine.
- TensorRT overhead = 34μs/call (83% of latency). Raw CUDA faster for simple models.
- Raw CUDA + 4 streams: 1.7M room-qps. TensorRT: 17K room-qps. 100× advantage.
- cuBLAS vs custom TC: 1,869 vs 97.6 GFLOPS at 256×256 (19× gap).
- Weight swap = 31,000× faster than engine rebuild: 1.2μs vs 310ms.
- Batch: 64 rooms = 0.057μs/room. 4096 rooms = 0.012μs/room.
- On-device TRT build = 0.3-1.5s. No cloud build server needed.
- GPU 95% idle: 40 TFLOPS theoretical, 1,869 GFLOPS measured.
- Thermal: 48-49°C sustained, passive cooling, 51°C to junction max.

## Environment
- nvcc: /usr/local/cuda-12.6/bin, nvidia-smi: /usr/sbin/nvidia-smi
- ARM64, no sudo, systemctl --user
- 8GB unified RAM, Python OOMs at ~6.5GB
- C11 compiles everywhere. Rust needs real machine. Claude Code OOMs 3+ parallel.

## Gotchas
- 68MB .git_backup dirs block git push — delete immediately
- DNS intermittent — 3 retries 5s backoff
- DeepSeek reliable at max_tokens 3500, 90s timeout
