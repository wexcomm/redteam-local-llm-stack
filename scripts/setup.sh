#!/usr/bin/env bash
set -e

echo "=========================================="
echo "🔴 RedTeam Local LLM Stack — Setup"
echo "=========================================="

# Detect environment
IS_WSL=false
if grep -qE "(Microsoft|WSL)" /proc/version 2>/dev/null; then
    IS_WSL=true
    echo "✅ WSL2 detected"
fi

# Detect GPU
GPU_VRAM="0"
GPU_NAME="none"
if command -v nvidia-smi &>/dev/null; then
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1 | xargs)
    GPU_VRAM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ')
    echo "🎮 GPU: $GPU_NAME (${GPU_VRAM}MB VRAM)"
else
    echo "⚠️  No NVIDIA GPU detected (CPU-only mode)"
fi

# Update packages
echo ""
echo "📦 Updating packages..."
sudo apt-get update -qq

# Install build dependencies
echo ""
echo "🔧 Installing build dependencies..."
sudo apt-get install -y -qq make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
    libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev \
    liblzma-dev git 2>/dev/null || true

# Install Python 3.11 if not present
if ! python3.11 --version &>/dev/null; then
    echo ""
    echo "🐍 Installing Python 3.11..."
    sudo apt-get install -y -qq python3.11 python3.11-venv python3.11-dev python3-pip
fi

# Install Poetry
if ! command -v poetry &>/dev/null; then
    echo ""
    echo "📜 Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
fi
export PATH="$HOME/.local/bin:$PATH"
poetry config virtualenvs.prefer-active-python true

# Install Ollama via snap if not present
if ! command -v ollama &>/dev/null; then
    echo ""
    echo "🦙 Installing Ollama..."
    sudo snap install ollama
fi
export PATH="/snap/bin:$PATH"

# Ensure Ollama is running
if ! curl -s http://localhost:11434/api/tags &>/dev/null; then
    echo ""
    echo "🚀 Starting Ollama..."
    ollama serve &
    sleep 3
fi

# Pull models
echo ""
echo "📥 Pulling models..."
ollama pull dolphin-mistral
ollama pull dolphin-llama3
ollama pull nomic-embed-text

# Create custom Modelfiles
echo ""
echo "🧠 Creating custom model personalities..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

ollama create redteam-analyst -f "$REPO_ROOT/config/modelfiles/redteam-analyst" 2>/dev/null || echo "  redteam-analyst already exists"
ollama create forensics-reviewer -f "$REPO_ROOT/config/modelfiles/forensics-reviewer" 2>/dev/null || echo "  forensics-reviewer already exists"
ollama create code-auditor -f "$REPO_ROOT/config/modelfiles/code-auditor" 2>/dev/null || echo "  code-auditor already exists"

# Clone PrivateGPT if not present
if [ ! -d "$HOME/privateGPT" ]; then
    echo ""
    echo "📂 Cloning PrivateGPT..."
    git clone https://github.com/zylon-ai/private-gpt.git "$HOME/privateGPT"
fi

cd "$HOME/privateGPT"

# Install dependencies
echo ""
echo "📚 Installing PrivateGPT dependencies..."
poetry install --extras "ui llms-ollama embeddings-ollama vector-stores-qdrant" 2>/dev/null || true

# Fix dependency hell
echo ""
echo "🔒 Pinning compatible llama-index versions..."
poetry run pip install -q "llama-index-core==0.11.23" \
    "llama-index-llms-ollama==0.3.6" \
    "llama-index-embeddings-ollama==0.3.1" \
    "llama-index-vector-stores-qdrant==0.3.3"

# Apply Gradio patch
echo ""
echo "🩹 Applying Gradio patch..."
python3 "$REPO_ROOT/privategpt-overrides/apply-gradio-patch.py" 2>/dev/null || echo "  Patch may already be applied"

# Run setup script
echo ""
echo "⚙️  Running PrivateGPT setup..."
poetry run python scripts/setup 2>/dev/null || echo "  Setup may have already run"

# Copy config
cp "$REPO_ROOT/config/settings-ollama.yaml" "$HOME/privateGPT/settings-ollama.yaml"

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo "=========================================="
echo ""
echo "Start the stack:"
echo "  cd ~/privateGPT"
echo "  PGPT_PROFILES=ollama poetry run python -m private_gpt"
echo ""
echo "Or use: ./scripts/start.sh"
echo ""
echo "Access:"
echo "  UI:    http://localhost:8283/"
echo "  API:   http://localhost:8283/docs"
echo ""
