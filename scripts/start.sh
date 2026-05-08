#!/usr/bin/env bash
set -e

echo "=========================================="
echo "🔴 Starting RedTeam Local LLM Stack"
echo "=========================================="

# Resolve Windows host IP for GPU Ollama
WINDOWS_HOST_IP=$(ip route | grep default | awk '{print $3}' | head -1)
if [ -z "$WINDOWS_HOST_IP" ]; then
    WINDOWS_HOST_IP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}' | head -1)
fi

echo "🎮 Windows GPU Ollama: http://$WINDOWS_HOST_IP:11434"

# Verify Windows Ollama is reachable
if ! curl -s --connect-timeout 3 "http://$WINDOWS_HOST_IP:11434/api/tags" &>/dev/null; then
    echo "❌ Windows Ollama not reachable at $WINDOWS_HOST_IP:11434"
    echo "   Make sure Windows Ollama is running:"
    echo "   - Check the Ollama tray icon on Windows"
    echo "   - Or run: ollama serve (from Windows PowerShell)"
    exit 1
fi

MODEL_COUNT=$(curl -s "http://$WINDOWS_HOST_IP:11434/api/tags" | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('models',[])))" 2>/dev/null || echo "?")
echo "🦙 Windows Ollama is running ($MODEL_COUNT models available)"

# Start PrivateGPT pointing to Windows GPU Ollama
echo ""
echo "🧠 Starting PrivateGPT with GPU inference..."
cd "$HOME/privateGPT"
export PATH="$HOME/.local/bin:$PATH"
export PATH="/snap/bin:$PATH"

echo "   Config: settings-ollama.yaml"
echo "   Ollama: http://$WINDOWS_HOST_IP:11434 (GPU)"
echo "   Port: 8283"
echo "   Profile: ollama"
echo ""

PGPT_PROFILES=ollama poetry run python -m private_gpt
