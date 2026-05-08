# 🏗️ Architecture

How the components of the RedTeam Local LLM Stack integrate.

---

## System Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACES                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ Gradio Web   │  │ Swagger API  │  │ Document Watchdog        │  │
│  │  (port 8283) │  │  (/docs)     │  │  (auto-ingest files)     │  │
│  └──────┬───────┘  └──────┬───────┘  └────────────┬─────────────┘  │
└─────────┼─────────────────┼───────────────────────┼────────────────┘
          │                 │                       │
          ▼                 ▼                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      PRIVATEGPT (Application Layer)                  │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  FastAPI Server (Uvicorn)                                   │   │
│  │  ├── Chat endpoint (RAG + uncensored LLM)                   │   │
│  │  ├── Ingest endpoint (document upload → vectors)            │   │
│  │  └── Query endpoint (document-only answers)                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                          │                                          │
│          ┌───────────────┼───────────────┐                         │
│          ▼               ▼               ▼                         │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ LLM        │  │ Embedding    │  │ Vector Store │              │
│  │ Component  │  │ Component    │  │ (Qdrant)     │              │
│  │ (Ollama)   │  │ (Ollama)     │  │              │              │
│  └─────┬──────┘  └──────┬───────┘  └──────┬───────┘              │
└────────┼────────────────┼─────────────────┼──────────────────────┘
         │                │                 │
         ▼                ▼                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      OLLAMA (Inference Engine)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ dolphin-     │  │ nomic-embed  │  │ Custom Modelfiles        │  │
│  │ mistral      │  │ -text        │  │ (redteam-analyst, etc.)  │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
│                                                                     │
│  Local GGUF weights ──► GPU/CPU inference ──► HTTP API (port 11434) │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### 1. Ollama (The Brain)

Ollama is the inference engine. It:
- Loads GGUF model weights into VRAM (or RAM if no GPU)
- Exposes an OpenAI-compatible HTTP API on port 11434
- Supports custom Modelfiles for task-specific personalities
- Handles both chat completion and embeddings

**Why Ollama?**
- Zero API costs
- Supports uncensored models (Dolphin, abliterated variants)
- Simple model management (`ollama pull`, `ollama run`)
- GPU passthrough works seamlessly in WSL2

### 2. PrivateGPT (The Application)

PrivateGPT is the RAG framework. It:
- Provides a web UI (Gradio) for chat and document upload
- Manages the ingestion pipeline (chunking → embedding → storage)
- Handles query routing (RAG retrieval + LLM generation)
- Supports multiple LLM backends (we use Ollama mode)

**Key modules:**
- `llm_component`: Connects to Ollama for text generation
- `embedding_component`: Connects to Ollama for vectorization
- `vectorstore_component`: Manages Qdrant (local file-based vector DB)
- `ui`: Gradio frontend

### 3. Qdrant (The Memory)

Qdrant stores document vectors locally:
- File-based (no separate server needed)
- Path: `local_data/private_gpt/qdrant/`
- Stores embeddings + metadata for each document chunk
- Enables semantic search across ingested documents

### 4. Document Watchdog (The Librarian)

Inspired by the Hermes Deal Monitor pattern:
- Watches a directory for new files (PDF, TXT, MD, etc.)
- Auto-ingests them into PrivateGPT via the API
- Scores documents by sensitivity keywords
- Logs all ingestion events

This bridges the gap between "I have a folder of threat intel PDFs" and "my AI knows about them."

### 5. Agent Bridge (The Hands — Concept)

Inspired by the Hermes Agentic CLI ReAct loop:
- Extends chat with tool execution capability
- Tools: file_read, file_write, terminal, code_execute
- LLM reasons → decides to use a tool → executes → observes → repeats

**Status:** Concept/bridge file. Full integration would require modifying PrivateGPT's chat endpoint to support tool loops. The pattern is documented in `tools/agent-bridge.py`.

---

## Data Flow

### Document Ingestion

```
User uploads PDF
    ↓
PrivateGPT splits into chunks (configurable size)
    ↓
Each chunk is sent to Ollama (nomic-embed-text) for embedding
    ↓
Embedding vector + metadata stored in Qdrant
    ↓
Document is now searchable via semantic similarity
```

### Chat with RAG

```
User asks: "What mitigation did the report suggest for CVE-2024-XXXX?"
    ↓
PrivateGPT embeds the query using nomic-embed-text
    ↓
Qdrant retrieves top-K similar document chunks
    ↓
Retrieved chunks + user query sent to Ollama (dolphin-mistral)
    ↓
LLM generates answer grounded in retrieved context
    ↓
User receives answer with source references
```

### Uncensored Analysis

```
User asks: "Generate a Python PoC for the heap spray technique in Figure 3"
    ↓
RAG retrieves Figure 3 context from uploaded paper
    ↓
LLM (uncensored dolphin-mistral) receives context + request
    ↓
No safety filters → generates the PoC code
    ↓
User receives working exploit code with technical annotations
```

---

## Security Boundaries

| Layer | Boundary | Notes |
|---|---|---|
| Network | `127.0.0.1` (localhost) | Use `0.0.0.0` only for WSL/Windows bridge |
| Data | WSL filesystem only | Documents never leave the WSL instance |
| Inference | Ollama local | No API calls to OpenAI/Anthropic |
| Models | User-pulled GGUFs | Verify hashes, pull from trusted sources |
| Tools | Working-directory scoped | Agent bridge restricts file ops to project dir |
