# Handoff Package: Red Team Local LLM Stack

> **Generated:** 2026-05-07  
> **For:** Next agent taking over this project  
> **Status:** All core services configured, both background tasks timed out (normal) and need restart

---

## 1. System Overview

### Hardware
- **GPU:** NVIDIA GTX 1650 4GB VRAM (Compute Capability 7.5)
- **Driver:** 595.79
- **OS:** Windows 11 host + WSL2 Ubuntu 24.04
- **Docker:** Installed in WSL with `nvidia` runtime available

### Network Architecture
```
Windows Host (172.21.16.1) <-- WSL2 NAT --> WSL Ubuntu
  |                                    |
  |- Ollama (0.0.0.0:11434)           |- PrivateGPT (0.0.0.0:8283)
  |- llama-server.exe (port 9001-9003) |
```
**Critical:** Windows `.exe` processes bind to Windows network stack. From WSL, access them via `172.21.16.1`, NOT `localhost`.

> **Note:** `172.21.16.1` is dynamic and may shift after WSL restart. Use `scripts/get-windows-host.sh` to auto-resolve.

---

## 2. Services & Ports

| Service | Port | Status | Start Command |
|---------|------|--------|---------------|
| Ollama | 11434 | ✅ GPU-accelerated | `ollama serve` (Windows service) |
| dolphin 2K | 9001 | ⚠️ Needs restart | `bash scripts/run-llama-dolphin.sh` |
| dolphin 4K | 9002 | ⚠️ Needs restart | `bash scripts/run-llama-dolphin-4k.sh` |
| Qwen 30B | 9003 | ⚠️ Needs restart | `bash scripts/run-llama-qwen.sh` |
| PrivateGPT | 8283 | ⚠️ Needs restart | `bash scripts/start.sh llamacpp-4k` |

### How to Start Everything

**Terminal 1 — Start LLM backend:**
```bash
cd /home/exo/redteam-local-llm-stack
bash scripts/run-llama-dolphin-4k.sh
```

**Terminal 2 — Start PrivateGPT:**
```bash
cd /home/exo/privateGPT
bash scripts/start.sh llamacpp-4k
```

PrivateGPT UI will be at: `http://localhost:8283`

---

## 3. Models

### dolphin-mistral 7B Q3_K_M
- **Location:** `C:\models\dolphin-mistral\dolphin-2.6-mistral-7b.Q3_K_M.gguf`
- **VRAM:** ~3.2GB at 4K context
- **Performance:** ~13 tok/s prompt, ~17 tok/s generation (GPU)
- **Configs:**
  - 2K context: `scripts/run-llama-dolphin.sh` (full GPU offload, `-ngl 999`)
  - 4K context: `scripts/run-llama-dolphin-4k.sh` (30 layers GPU, 3 on CPU)

### Qwen3-30B-A3B (abliterated)
- **Location:** `C:\models\qwen-35b\Qwen3-30B-A3B-abliterated-erotic.i1-Q4_K_S.gguf`
- **Size:** 17.5GB
- **Performance:** ~0.5 tok/s (CPU experts bottleneck with `--cpu-moe`)
- **Start:** `bash scripts/run-llama-qwen.sh`

### Ollama Models
- `dolphin-mistral:latest` (via Ollama pull)
- `nomic-embed-text` (for embeddings)

---

## 4. Git Repositories

### Repo 1: redteam-local-llm-stack
- **GitHub:** `https://github.com/wexcomm/redteam-local-llm-stack`
- **Local:** `/home/exo/redteam-local-llm-stack`
- **Status:** ✅ Pushed to GitHub (commit `b55c489`)
- **Contents:** Scripts, configs, documentation, skill files

### Repo 2: privateGPT (FORK REQUIRED)
- **Upstream:** `zylon-ai/private-gpt`
- **Local:** `/home/exo/privateGPT`
- **Status:** ⚠️ Local commits only (commit `ec6ce65`), NOT pushed to GitHub fork
- **Git bundle backup:** 
  - Local: `/home/exo/privateGPT-backup.bundle` (2.7MB)
  - **Also backed up in:** `wexcomm/redteam-local-llm-stack` repo (commit `d2a297a`)
  - Contains full repo with all commits — can be cloned anywhere
- **Action needed:** Create fork under `wexcomm/private-gpt` on GitHub, then push

**To push privateGPT commits:**
```bash
cd /home/exo/privateGPT
git remote add myfork https://github.com/wexcomm/private-gpt.git
git push myfork main
```

**To restore from bundle (if needed):**
```bash
# From local WSL
git clone /home/exo/privateGPT-backup.bundle privateGPT-restored

# Or download from GitHub
curl -L https://github.com/wexcomm/redteam-local-llm-stack/raw/master/privateGPT-backup.bundle -o privateGPT-backup.bundle
git clone privateGPT-backup.bundle privateGPT-restored
```

---

## 5. Key Configuration Files

### PrivateGPT Settings
| File | Purpose |
|------|---------|
| `settings-llamacpp-4k.yaml` | dolphin 4K via OpenAI-compatible API (port 9002) |
| `settings-llamacpp-server.yaml` | dolphin 2K via OpenAI-compatible API (port 9001) |
| `settings-llamacpp-qwen.yaml` | Qwen via OpenAI-compatible API (port 9003) |
| `settings-llamacpp-native-4k.yaml` | Native llama.cpp mode (not OpenAI API) |
| `settings-ollama.yaml` | Ollama backend mode |

### Critical Patches

**qdrant_compat.py** — Monkey-patch for qdrant-client 1.17+
- Location: `/home/exo/privateGPT/qdrant_compat.py`
- Imported in: `/home/exo/privateGPT/private_gpt/__main__.py`
- Fixes: Restores `search()` / `search_batch()` API for llama-index-vector-stores-qdrant 0.3.3

**ingest_component.py** — Remove `show_progress=True`
- Location: `/home/exo/privateGPT/private_gpt/components/ingest/ingest_component.py`
- Lines: 142, 212, 294
- Fixes: llama-index-core 0.11.23 incompatibility

---

## 6. Known Issues & Workarounds

| Issue | Workaround |
|-------|-----------|
| qdrant-client 1.17+ API breaking change | `qdrant_compat.py` monkey-patch |
| llama-index-core 0.11.23 `show_progress` removed | Removed from `ingest_component.py` |
| Windows `.exe` network binding | Use `172.21.16.1` from WSL, not `localhost` |
| Dynamic WSL host IP | Use `scripts/get-windows-host.sh` to resolve |
| `turbo4`/`turbo3` KV cache types don't exist | Using `q4_0` instead (mainline llama.cpp b9082) |
| searchsploit install timed out | Can retry `sudo apt install exploitdb` or use git clone |
| PrivateGPT not pushed to GitHub | Need to create fork of `zylon-ai/private-gpt` |

---

## 7. Dependency Pins

These specific versions are required for compatibility:
```
llama-index-core==0.11.23
llama-index-llms-ollama==0.3.6
qdrant-client==1.17.1
```

OpenAI extras installed:
```bash
cd /home/exo/privateGPT && poetry install --extras llms-openai
```

---

## 8. File Locations

### Windows Paths (accessible from WSL via `/mnt/c/`)
```
C:\llama-cpp\                    # llama.cpp CUDA binary (b9082, CUDA 12.4)
C:\models\dolphin-mistral\       # dolphin-mistral 7B Q3_K_M
C:\models\qwen-35b\              # Qwen3-30B-A3B Q4_K_S
```

### WSL Paths
```
/home/exo/redteam-local-llm-stack/    # Main project repo
/home/exo/privateGPT/                  # PrivateGPT fork (local commits)
/home/exo/.local/bin/poetry           # Poetry package manager
```

---

## 9. Quick Commands

```bash
# Check GPU status
nvidia-smi

# Get Windows host IP from WSL
bash scripts/get-windows-host.sh

# Test dolphin server
curl http://172.21.16.1:9002/v1/models

# Test PrivateGPT health
curl http://localhost:8283/health

# Switch PrivateGPT profile
bash scripts/start.sh llamacpp-2k   # 2K context
bash scripts/start.sh llamacpp-4k   # 4K context
bash scripts/start.sh qwen          # Qwen model
bash scripts/start.sh ollama        # Ollama backend
```

---

## 10. Next Steps for New Agent

1. **Restart services** (both timed out and need restart):
   - `bash scripts/run-llama-dolphin-4k.sh` (background)
   - `bash scripts/start.sh llamacpp-4k` (background)

2. **Create GitHub fork** for privateGPT and push local commits

3. **Install searchsploit** if needed for red team ops:
   ```bash
   sudo apt update && sudo apt install exploitdb
   ```

4. **Verify end-to-end** — Open PrivateGPT UI, send a test message, confirm response

5. **Optional:** Set up systemd/tmux for persistent services

---

*End of handoff package*
