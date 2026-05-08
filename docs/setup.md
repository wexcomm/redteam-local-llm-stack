# 🖥️ Setup Guide — RedTeam Local LLM Stack

Complete installation for WSL2 Ubuntu with NVIDIA GPU passthrough.

---

## 📋 Prerequisites

- Windows 10/11 with WSL2
- NVIDIA GPU (GTX 10-series or newer)
- 16GB+ RAM recommended
- 30GB+ free disk space

---

## Phase 1: WSL2 + GPU Validation

```bash
# Verify WSL2 and GPU passthrough
nvidia-smi
# Should show your GPU name, driver version, and VRAM
```

If `nvidia-smi` fails:
1. Install NVIDIA drivers on Windows: https://www.nvidia.com/Download/index.aspx
2. Restart WSL: `wsl --shutdown` then reopen WSL

---

## Phase 2: Ollama (Inference Engine)

```bash
# Install Ollama via snap
sudo snap install ollama

# Add to PATH
export PATH="/snap/bin:$PATH"

# Verify
ollama --version
```

### Pull Models

```bash
# Uncensored models for red teaming
ollama pull dolphin-mistral      # Fast, good reasoning
ollama pull dolphin-llama3       # Stronger coding/analysis
ollama pull nomic-embed-text     # Document embeddings

# Optional: coding specialist
ollama pull qwen2.5-coder:14b
```

### Create Custom Personalities (Modelfiles)

```bash
# From this repo
cd ~/redteam-local-llm-stack
ollama create redteam-analyst -f config/modelfiles/redteam-analyst
ollama create forensics-reviewer -f config/modelfiles/forensics-reviewer
ollama create code-auditor -f config/modelfiles/code-auditor
```

---

## Phase 3: Python Environment

```bash
# Install build deps (for pyenv if you want isolation)
sudo apt-get update
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
    libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev

# Install pyenv (optional but recommended)
curl https://pyenv.run | bash
# Add to ~/.bashrc as instructed, then restart shell
pyenv install 3.11
pyenv local 3.11

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
poetry config virtualenvs.prefer-active-python true
```

---

## Phase 4: PrivateGPT

```bash
# Clone PrivateGPT
git clone https://github.com/zylon-ai/private-gpt.git ~/privateGPT
cd ~/privateGPT

# Install with Ollama + Qdrant extras
poetry install --extras "ui llms-ollama embeddings-ollama vector-stores-qdrant"

# Fix dependency hell: pin compatible llama-index versions
poetry run pip install "llama-index-core==0.11.23" \
    "llama-index-llms-ollama==0.3.6" \
    "llama-index-embeddings-ollama==0.3.1" \
    "llama-index-vector-stores-qdrant==0.3.3"

# Run setup script (downloads embedding model)
poetry run python scripts/setup
```

### Apply Gradio Patch

PrivateGPT uses Gradio for its UI. A bug in `gradio-client` causes a `TypeError` when JSON schema contains boolean values.

```bash
# Patch is included in this repo
cd ~/redteam-local-llm-stack
python3 privategpt-overrides/apply-gradio-patch.py
```

### Copy Configuration

```bash
cp ~/redteam-local-llm-stack/config/settings-ollama.yaml ~/privateGPT/settings-ollama.yaml
```

---

## Phase 5: Start the Stack

```bash
cd ~/privateGPT
PGPT_PROFILES=ollama poetry run python -m private_gpt
```

Access:
- **Chat UI**: http://localhost:8283/
- **API Docs**: http://localhost:8283/docs

---

## Phase 6: Document Watchdog (Optional)

Auto-ingest new files into your RAG knowledge base:

```bash
# Install watchdog dependency
pip install watchdog

# Run the watchdog
python3 ~/redteam-local-llm-stack/tools/document-watchdog.py \
    --watch ~/Documents/redteam-data \
    --api http://localhost:8281
```

---

## 🐛 Troubleshooting

### Port 8001 already in use
Change `port: 8001` to `port: 8283` (or any free port) in `settings-ollama.yaml`.

### Gradio "bool is not iterable" error
The patch was not applied. Re-run the patch script from Phase 4.

### Ollama connection refused
Ensure Ollama is running: `systemctl status ollama` or `ollama serve`

### Out of VRAM
- Use smaller models: `dolphin-mistral` instead of `dolphin-llama3`
- Reduce `context_window` in settings
- Reduce `max_new_tokens`

### Python lzma error during pyenv install
```bash
sudo apt-get install liblzma-dev
pyenv install 3.11
```
