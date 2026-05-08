# 🔴 RedTeam Local LLM Stack

> A sovereign, air-gapped AI infrastructure for offensive security research, red teaming, and sensitive document analysis. Built on **Ollama** + **PrivateGPT** with ideas from the Hermes Ollama Agent hybrid-assistant architecture.

---

## 🎯 What This Is

| Capability | Commercial AI (ChatGPT/Claude) | This Stack |
|---|---|---|
| **Data Privacy** | ❌ Sent to cloud | ✅ Never leaves localhost |
| **Refusal Barriers** | ❌ Hard refusals on exploit PoCs | ✅ Uncensored, obeys instructions |
| **Proprietary Docs** | ❌ Policy violation to upload | ✅ Local RAG ingestion |
| **Tool Use** | ❌ Limited/controlled | ✅ Agent bridge for file ops, terminal, code execution |
| **Cost** | $20-200/mo API | **$0** after setup |
| **Custom Models** | ❌ Vendor-controlled | ✅ Custom Modelfiles for specific tasks |

**This stack combines three disciplines:**
1. **Local Inference** (Ollama) — uncensored models, zero API costs
2. **Retrieval Augmented Generation** (PrivateGPT) — your documents, your vectors, your answers
3. **Agentic Action** (inspired by Hermes Agentic CLI) — LLM that does not just chat, it *does*

---

## 📁 Project Structure

```
redteam-local-llm-stack/
├── README.md                          # This file
├── docs/
│   ├── setup.md                       # Full installation guide
│   ├── architecture.md                # How components integrate
│   └── red-teaming-guide.md           # Security research workflows
├── config/
│   ├── settings-ollama.yaml           # PrivateGPT configuration
│   └── modelfiles/
│       ├── redteam-analyst            # Exploit analysis & PoC generation
│       ├── forensics-reviewer         # Log analysis & incident response
│       └── code-auditor               # Vulnerability discovery in source
├── tools/
│   ├── document-watchdog.py           # Auto-ingest new files into RAG
│   └── agent-bridge.py                # Concept: LLM-driven tool execution
├── scripts/
│   ├── setup.sh                       # One-command WSL setup
│   └── start.sh                       # Start the stack
└── privategpt-overrides/              # Patches for PrivateGPT issues
    └── gradio-client-bool-fix.patch   # Fixes Gradio TypeError
```

---

## 🚀 Quick Start

```bash
# 1. Clone this repo
git clone <your-fork-url> ~/redteam-local-llm-stack
cd ~/redteam-local-llm-stack

# 2. Run unified setup (detects GPU, installs deps, patches issues)
./scripts/setup.sh

# 3. Start everything
./scripts/start.sh

# 4. Open the UI
# http://localhost:8283/          — PrivateGPT chat + RAG
# http://localhost:8283/docs      — API documentation
```

See [docs/setup.md](docs/setup.md) for detailed installation.

---

## 🧠 Models & Personalities

We use **Ollama Modelfiles** to create task-specific model personalities. Unlike system prompts alone, Modelfiles bake the behavior into the model weights at runtime.

| Modelfile | Purpose | Base Model |
|---|---|---|
| `redteam-analyst` | Exploit PoC generation, payload crafting, attack chain analysis | dolphin-mistral |
| `forensics-reviewer` | Log analysis, timeline reconstruction, IOC extraction | dolphin-llama3 |
| `code-auditor` | Source code review, vulnerability discovery, secure coding guidance | qwen2.5-coder |

Create a model:
```bash
ollama create redteam-analyst -f config/modelfiles/redteam-analyst
ollama run redteam-analyst
```

---

## 📚 Documentation

- **[Setup Guide](docs/setup.md)** — WSL2, GPU passthrough, Ollama, PrivateGPT, dependency resolution
- **[Architecture](docs/architecture.md)** — How Ollama, PrivateGPT, Qdrant, and the agent bridge fit together
- **[Red Teaming Guide](docs/red-teaming-guide.md)** — Workflows: document ingestion, Query vs Chat mode, uncensored PoC generation, OPSEC rules

---

## 🔧 Key Integrations from Hermes

| Hermes Component | Our Adaptation |
|---|---|
| Agentic CLI (ReAct + tools) | `tools/agent-bridge.py` — concept for extending PrivateGPT with tool execution |
| Deal Monitor (watch + score + alert) | `tools/document-watchdog.py` — watches directories, auto-ingests into RAG, scores by sensitivity |
| WSL GPU auto-detection | `scripts/setup.sh` — detects VRAM, configures optimal context/gpu_layers |
| Docker Compose orchestration | Native WSL services (no Docker overhead for single-machine use) |
| YAML config hierarchy | Enhanced `config/settings-ollama.yaml` with sections for models, toolsets, features |

---

## ⚠️ OPSEC Rules

1. **Air-gap by default** — `host: 127.0.0.1` in production; `0.0.0.0` only for WSL/Windows bridge
2. **No cloud APIs** — All inference is local. No OpenAI, no Anthropic, no telemetry.
3. **Document isolation** — Ingested documents live in `local_data/private_gpt/qdrant/` only.
4. **Model provenance** — Only use models you pulled yourself. Verify GGUF hashes when possible.

---

## 📝 License

MIT — Built for the security research community. Use responsibly.
