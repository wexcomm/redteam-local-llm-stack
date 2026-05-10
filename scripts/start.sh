#!/usr/bin/env bash
set -e

MODE="${1:-llamacpp-2k}"

echo "=========================================="
echo "🔴 Starting RedTeam Local LLM Stack"
echo "=========================================="

# Resolve Windows host IP for GPU Ollama
WINDOWS_HOST_IP=$(ip route | grep default | awk '{print $3}' | head -1)
if [ -z "$WINDOWS_HOST_IP" ]; then
    WINDOWS_HOST_IP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}' | head -1)
fi

cd "$HOME/privateGPT"
export PATH="$HOME/.local/bin:$PATH"
export PATH="/snap/bin:$PATH"

if [ "$MODE" = "ollama" ]; then
    echo "🎮 Mode: Ollama (Windows GPU)"
    echo "   Ollama: http://$WINDOWS_HOST_IP:11434"
    
    if ! curl -s --connect-timeout 3 "http://$WINDOWS_HOST_IP:11434/api/tags" &>/dev/null; then
        echo "❌ Windows Ollama not reachable at $WINDOWS_HOST_IP:11434"
        exit 1
    fi
    
    MODEL_COUNT=$(curl -s "http://$WINDOWS_HOST_IP:11434/api/tags" | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('models',[])))" 2>/dev/null || echo "?")
    echo "🦙 Windows Ollama is running ($MODEL_COUNT models available)"
    echo "   Config: settings-ollama.yaml"
    echo "   Port: 8283"
    echo ""
    
    PGPT_PROFILES=ollama /home/exo/.local/bin/poetry run python -m private_gpt

elif [ "$MODE" = "llamacpp-2k" ] || [ "$MODE" = "llamacpp" ]; then
    echo "🎮 Mode: llama.cpp dolphin 2K context (fast, full GPU offload)"
    echo "   LLM:    http://$WINDOWS_HOST_IP:9001 (dolphin-mistral 7B, ctx 2048)"
    echo "   Embeds: http://$WINDOWS_HOST_IP:11434 (Ollama nomic-embed-text)"
    echo "   Config: settings-llamacpp-server.yaml"
    echo "   Port: 8283"
    echo ""
    
    if ! curl -s --connect-timeout 3 "http://$WINDOWS_HOST_IP:9001/health" &>/dev/null; then
        echo "⚠️  dolphin llama-server not running on port 9001"
        echo "   Start it with: bash scripts/run-llama-dolphin.sh"
        exit 1
    fi
    echo "✅ dolphin llama-server reachable (port 9001)"
    
    if ! curl -s --connect-timeout 3 "http://$WINDOWS_HOST_IP:11434/api/tags" &>/dev/null; then
        echo "⚠️  Windows Ollama not reachable for embeddings"
        exit 1
    fi
    echo "✅ Ollama embeddings reachable"
    echo ""
    
    PGPT_PROFILES=llamacpp-server /home/exo/.local/bin/poetry run python -m private_gpt

elif [ "$MODE" = "llamacpp-4k" ]; then
    echo "🎮 Mode: llama.cpp dolphin 4K context (larger context, 30 GPU layers)"
    echo "   LLM:    http://$WINDOWS_HOST_IP:9002 (dolphin-mistral 7B, ctx 4096)"
    echo "   Embeds: http://$WINDOWS_HOST_IP:11434 (Ollama nomic-embed-text)"
    echo "   Config: settings-llamacpp-4k.yaml"
    echo "   Port: 8283"
    echo ""
    
    if ! curl -s --connect-timeout 3 "http://$WINDOWS_HOST_IP:9002/health" &>/dev/null; then
        echo "⚠️  dolphin-4k llama-server not running on port 9002"
        echo "   Start it with: bash scripts/run-llama-dolphin-4k.sh"
        exit 1
    fi
    echo "✅ dolphin-4k llama-server reachable (port 9002)"
    
    if ! curl -s --connect-timeout 3 "http://$WINDOWS_HOST_IP:11434/api/tags" &>/dev/null; then
        echo "⚠️  Windows Ollama not reachable for embeddings"
        exit 1
    fi
    echo "✅ Ollama embeddings reachable"
    echo ""
    
    PGPT_PROFILES=llamacpp-4k /home/exo/.local/bin/poetry run python -m private_gpt

elif [ "$MODE" = "qwen" ]; then
    echo "🎮 Mode: llama.cpp Qwen 30B MoE (slow, high capability)"
    echo "   LLM:    http://$WINDOWS_HOST_IP:9003 (Qwen3-30B-A3B, ctx 4096)"
    echo "   Embeds: http://$WINDOWS_HOST_IP:11434 (Ollama nomic-embed-text)"
    echo "   Config: settings-llamacpp-qwen.yaml"
    echo "   Port: 8283"
    echo ""
    
    if ! curl -s --connect-timeout 3 "http://$WINDOWS_HOST_IP:9003/health" &>/dev/null; then
        echo "⚠️  Qwen llama-server not running on port 9003"
        echo "   Start it with: bash scripts/run-llama-qwen.sh"
        exit 1
    fi
    echo "✅ Qwen llama-server reachable (port 9003)"
    
    if ! curl -s --connect-timeout 3 "http://$WINDOWS_HOST_IP:11434/api/tags" &>/dev/null; then
        echo "⚠️  Windows Ollama not reachable for embeddings"
        exit 1
    fi
    echo "✅ Ollama embeddings reachable"
    echo ""
    
    PGPT_PROFILES=llamacpp-qwen /home/exo/.local/bin/poetry run python -m private_gpt

else
    echo "Usage: $0 [ollama|llamacpp-2k|llamacpp-4k|qwen]"
    echo "  ollama      - Use Windows Ollama for both LLM and embeddings"
    echo "  llamacpp-2k - Use dolphin-mistral 7B with 2048 ctx (fast, default)"
    echo "  llamacpp-4k - Use dolphin-mistral 7B with 4096 ctx (larger context)"
    echo "  qwen        - Use Qwen3-30B-A3B MoE (slow but high capability)"
    exit 1
fi
