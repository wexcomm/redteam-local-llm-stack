#!/bin/bash
# Run dolphin-mistral 7B Q3_K_M with 4096 context window on GTX 1650 4GB
# Uses reduced GPU offload (-ngl 30) to fit larger context in VRAM
# Uses Windows llama.cpp binary via WSL (CUDA runtime bundled)

LLAMA_BIN=/mnt/c/llama-cpp/llama-server.exe
MODEL=C:/models/dolphin-mistral/dolphin-2.6-mistral-7b.Q3_K_M.gguf
HOST=0.0.0.0
PORT=9002

# Context size: 4096 needs reduced GPU layers to fit in 4GB VRAM
# -ngl 30 = offload 30/33 layers to GPU (3 layers on CPU)
# --no-mmap = load weights into VRAM/RAM directly
# --cache-type-k/v q4_0 = quantize KV cache to 4-bit
# NOTE: --mlock causes OOM on 4GB; omitted.

exec "$LLAMA_BIN" \
    --model "$MODEL" \
    --ctx-size 4096 \
    -ngl 30 \
    --no-mmap \
    --cache-type-k q4_0 \
    --cache-type-v q4_0 \
    --host "$HOST" \
    --port "$PORT" \
    "$@"
