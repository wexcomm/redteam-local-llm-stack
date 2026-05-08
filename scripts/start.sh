#!/usr/bin/env bash
set -e

echo "=========================================="
echo "🔴 Starting RedTeam Local LLM Stack"
echo "=========================================="

# Ensure Ollama is running
if ! curl -s http://localhost:11434/api/tags &>/dev/null; then
    echo "🚀 Starting Ollama..."
    ollama serve &
    sleep 3
fi

echo "🦙 Ollama is running"
ollama list

echo ""
echo "🧠 Starting PrivateGPT..."
cd "$HOME/privateGPT"
export PATH="$HOME/.local/bin:$PATH"
export PATH="/snap/bin:$PATH"

echo "   Config: settings-ollama.yaml"
echo "   Port: 8283"
echo "   Profile: ollama"
echo ""

PGPT_PROFILES=ollama poetry run python -m private_gpt
