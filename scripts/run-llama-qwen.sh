#!/bin/bash
# Run Qwen3-30B-A3B abliterated on GTX 1650 4GB with MoE expert CPU offloading
# Uses Windows llama.cpp binary via WSL (CUDA runtime bundled)
# Model: mradermacher/Qwen3-30B-A3B-abliterated-erotic-i1-GGUF

LLAMA_BIN=/mnt/c/llama-cpp/llama-server.exe
MODEL=C:/models/qwen-35b/Qwen3-30B-A3B-abliterated-erotic.i1-Q4_K_S.gguf
HOST=0.0.0.0
PORT=9003

# Qwen3-30B-A3B is a Mixture-of-Experts (MoE) model (~17.5GB Q4_K_S).
# Dense offload to 4GB VRAM is impossible.
# Strategy: offload ALL expert weights to CPU, keep attention on GPU.
#
# --cpu-moe = keep ALL MoE expert weights on CPU (not just first N layers)
# -ngl 999 = offload all non-expert layers (attention, norms, embeddings) to GPU
# --no-mmap = load weights into RAM directly
# --cache-type-k/v q4_0 = quantize KV cache to save VRAM
# -c 4096 = context window (fits comfortably in 4GB)
#
# Performance on GTX 1650 4GB:
#   Prompt processing: ~0.48 tok/s (CPU-bound expert routing)
#   Generation: ~0.57 tok/s
#   VRAM usage: ~1.2 GB (778MB model + 108MB KV + 300MB compute)
#   System RAM usage: ~15.3GB (expert weights on CPU)
#
# NOTE: turbo4/turbo3 KV cache types from the video are NOT in mainline llama.cpp b9082
#       q4_0 is the best available alternative.
# NOTE: --mlock causes OOM on 4GB; omitted.
# NOTE: Video suggested --n-cpu-moe 35, but with 4GB VRAM we need --cpu-moe
#       to fit. If you have more VRAM, try --n-cpu-moe 45 or 35.

exec "$LLAMA_BIN" \
    --model "$MODEL" \
    --ctx-size 4096 \
    -ngl 999 \
    --cpu-moe \
    --no-mmap \
    --cache-type-k q4_0 \
    --cache-type-v q4_0 \
    --host "$HOST" \
    --port "$PORT" \
    "$@"
