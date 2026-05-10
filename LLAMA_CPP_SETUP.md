# llama.cpp CUDA Setup & Model Optimization Notes

## Environment
- WSL2 Ubuntu 24.04 on Windows 11
- NVIDIA GTX 1650 4GB VRAM (Compute Capability 7.5, no tensor cores)
- Driver: 595.79
- Windows host IP from WSL: `172.21.16.1` (dynamic, check with `scripts/get-windows-host.sh`)

## llama.cpp Binary
**Source:** Pre-built Windows CUDA binary from GitHub releases  
**Version:** b9082  
**Location:** `C:\llama-cpp\` (Windows path, accessible from WSL as `/mnt/c/llama-cpp/`)

**Why Windows binary?**
- Native WSL build requires `nvcc` (CUDA toolkit) — `apt install` timed out after 600s
- Pre-built Linux CUDA binaries are not published by llama.cpp
- Docker images (`ghcr.io/ggerganov/llama.cpp:server-cuda`, `docker.io/yusiwen/llama.cpp:cuda`) were not found
- Windows binary bundles `cudart64_12.dll`, `cublas64_12.dll` — works from WSL via WSL->Windows interop

**Key executables:**
- `/mnt/c/llama-cpp/llama-server.exe` — OpenAI-compatible HTTP API server
- `/mnt/c/llama-cpp/llama-cli.exe` — Interactive CLI

## Important: Networking Quirk
Windows `.exe` processes launched from WSL bind to the **Windows host network stack**, not WSL's.
- Server bound to `0.0.0.0:8080` from WSL is reachable at `http://172.21.16.1:8080` from WSL
- `localhost:8080` or `127.0.0.1:8080` from WSL **will NOT work**
- From Windows host itself, use `localhost:8080`

---

## Model Path 1: dolphin-mistral 7B Q3_K_M (Dense Transformer)

**Use case:** General red team assistant, uncensored, fits in 4GB VRAM  
**Model file:** `C:/models/dolphin-mistral/dolphin-2.6-mistral-7b.Q3_K_M.gguf` (~3.3GB)  
**Server port:** 8080

### Working Flags
```bash
/mnt/c/llama-cpp/llama-server.exe \
    --model C:/models/dolphin-mistral/dolphin-2.6-mistral-7b.Q3_K_M.gguf \
    --ctx-size 2048 \
    -ngl 999 \
    --no-mmap \
    --cache-type-k q4_0 \
    --cache-type-v q4_0 \
    --host 0.0.0.0 --port 8080
```

| Flag | Purpose | Status |
|------|---------|--------|
| `-ngl 999` | Full GPU offload | ✅ Working |
| `--no-mmap` | Load weights into memory directly | ✅ Working |
| `--mlock` | Pin memory (prevent swapping) | ❌ OOM on 4GB — omitted |
| `--cache-type-k turbo4` | Video's KV cache quant for K | ❌ **NOT in mainline llama.cpp** |
| `--cache-type-v turbo3` | Video's KV cache quant for V | ❌ **NOT in mainline llama.cpp** |
| `--cache-type-k q4_0` | Best available KV K quant | ✅ Working, saves VRAM |
| `--cache-type-v q4_0` | Best available KV V quant | ✅ Working, saves VRAM |

### Performance (GTX 1650)
- Prompt processing: **56.3 tok/s**
- Generation: **19.7 tok/s**
- Context: 2048 tokens
- VRAM usage: fits within 4095 MiB total

### Why ctx-size 2048?
At 4096 with `--mlock`, the model+KV cache+compute buffer needed ~3553 MiB but only ~3297 MiB was free (Windows display uses ~800MB). Reducing to 2048 and dropping `--mlock` made it fit.

### Wrapper Script
```bash
/home/exo/redteam-local-llm-stack/scripts/run-llama-dolphin.sh
```

---

## Model Path 2: Qwen3-30B-A3B Abliterated (MoE) — ✅ TESTED & WORKING

**Use case:** High-capability uncensored model with tool-use / reasoning  
**Model file:** `Qwen3-30B-A3B-abliterated-erotic.i1-Q4_K_S.gguf` (~16.25 GiB / 4.57 BPW)  
**Source:** `mradermacher/Qwen3-30B-A3B-abliterated-erotic-i1-GGUF`  
**Server port:** 8081

### Architecture
- **Total params:** 30.53 B
- **Active params per token:** ~3.3 B (A3B = Active 3 Billion)
- **Layers:** 48
- **Experts:** 128 per layer, 8 used per token
- **Context (trained):** 40960

### About Abliteration
- **Raw abliteration** (weight-level guardrail removal) **breaks MoE circuits** — degrades reasoning and tool-use
- **Post-ablation finetuning ("healing")** restores capability
- `mradermacher/Qwen3-30B-A3B-abliterated-erotic-i1-GGUF` is **pre-healed** — preferred over raw `huihui_ai` abliterated variants

### Working Flags
```bash
/mnt/c/llama-cpp/llama-server.exe \
    --model C:/models/qwen-35b/Qwen3-30B-A3B-abliterated-erotic.i1-Q4_K_S.gguf \
    --ctx-size 4096 \
    -ngl 999 \
    --cpu-moe \
    --no-mmap \
    --cache-type-k q4_0 \
    --cache-type-v q4_0 \
    --host 0.0.0.0 --port 8081
```

| Flag | Purpose | Status |
|------|---------|--------|
| `--cpu-moe` | ALL MoE expert weights on CPU | ✅ Working — required for 4GB VRAM |
| `--n-cpu-moe 35` | First 35 layers' experts on CPU | ⚠️ Video suggestion, but with 4GB we need `--cpu-moe` |
| `-ngl 999` | All attention/norm/emb layers on GPU | ✅ Working |
| `--no-mmap` | Load weights into RAM directly | ✅ Working |
| `--mlock` | Pin memory | ❌ OOM risk — omitted |
| `--cache-type-k/v q4_0` | KV cache quantization | ✅ Working (turbo4/3 unavailable) |

### Memory Breakdown
| Component | Location | Size |
|-----------|----------|------|
| Model weights (attention, norms, embeddings) | GPU | 778.73 MiB |
| Model weights (128 experts × 48 layers) | CPU RAM | 15,696 MiB (~15.3 GB) |
| KV cache (4096 ctx, q4_0) | GPU | 108 MiB |
| Compute buffer | GPU | 300.75 MiB |
| **Total GPU usage** | GPU | **~1,187 MiB** |
| **Free GPU after load** | GPU | **~2,109 MiB** |

### Performance (GTX 1650)
| Phase | Speed | Notes |
|-------|-------|-------|
| Prompt processing | **0.48 tok/s** | Very slow — CPU-bound expert routing for every token |
| Generation | **0.57 tok/s** | Slow but usable for short responses |
| First load time | ~30-60s | Loading 15.3GB of experts into CPU RAM |

**Why so slow?** With `--cpu-moe`, every token must route through CPU-loaded expert weights. The GTX 1650 has no tensor cores and the CPU→GPU data transfer for expert activations is bandwidth-limited.

### Optimizations to Try (if more VRAM available)
If you upgrade to a card with 8GB+ VRAM:
- Replace `--cpu-moe` with `--n-cpu-moe 45` (only 3 layers' experts on GPU)
- This would dramatically speed up prompt processing
- Could also increase `--ctx-size` to 8192 or 16384

### Wrapper Script
```bash
/home/exo/redteam-local-llm-stack/scripts/run-llama-qwen.sh
```

---

## Video Claims vs Reality

The Codacus video recommended 5 flags for Qwen 35B on llama.cpp:

| Video Claim | Reality in llama.cpp b9082 |
|-------------|---------------------------|
| `--n-cpu-moe 35` | ✅ Exists, but for 4GB VRAM we need `--cpu-moe` |
| `--no-mmap` | ✅ Exists, works |
| `--mlock` | ✅ Exists, but OOMs on 4GB — use with caution |
| `--cache-type-k turbo4` | ❌ **Does NOT exist** — use `q4_0` instead |
| `--cache-type-v turbo3` | ❌ **Does NOT exist** — use `q4_0` instead |
| `-c 262144` | ⚠️ Exists, but 262K context would OOM instantly on 4GB — use 2048-4096 |

**Speculative decoding:** Video noted it fails for MoE+SSM but works for dense transformers. We didn't test this.

---

## Quick Test

```bash
# Start dolphin server
bash /home/exo/redteam-local-llm-stack/scripts/run-llama-dolphin.sh

# In another terminal, test via Windows host IP
curl http://172.21.16.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 50
  }'

# Start Qwen server
bash /home/exo/redteam-local-llm-stack/scripts/run-llama-qwen.sh

# Test Qwen (slower response, be patient)
curl http://172.21.16.1:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 50
  }'
```

## Current Status
- [x] llama.cpp with CUDA working via Windows binary
- [x] dolphin-mistral 7B Q3_K_M tested (56 tok/s prompt, 20 tok/s gen)
- [x] Qwen3-30B-A3B abliterated downloaded, copied, and tested (0.5 tok/s)
- [x] Wrapper scripts created for both models
- [ ] Optional: Test `--n-cpu-moe` variants if more VRAM becomes available
