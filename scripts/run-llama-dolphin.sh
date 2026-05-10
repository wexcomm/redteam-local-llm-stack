#!/bin/bash
# Run dolphin-mistral 7B Q3_K_M on GTX 1650 4GB with full GPU offload
# Uses Windows llama.cpp binary via WSL (CUDA runtime bundled)

LLAMA_BIN=/mnt/c/llama-cpp/llama-server.exe
MODEL=C:/models/dolphin-mistral/dolphin-2.6-mistral-7b.Q3_K_M.gguf
HOST=0.0.0.0
PORT=9001

# Context size: 2048 fits in 4GB VRAM with Q3_K_M weights + q4_0 KV cache
# -ngl 999 = full GPU offload
# --no-mmap = load weights into VRAM/RAM directly
# --cache-type-k/v q4_0 = quantize KV cache to 4-bit (saves ~50% VRAM vs f16)
# NOTE: turbo4/turbo3 from the video are NOT available in mainline llama.cpp b9082
#       q4_0 is the best available alternative for VRAM-constrained setups

exec "$LLAMA_BIN" \
    --model "$MODEL" \
    --ctx-size 2048 \
    -ngl 999 \
    --no-mmap \
    --cache-type-k q4_0 \
    --cache-type-v q4_0 \
    --host "$HOST" \
    --port "$PORT" \
    "$@"
