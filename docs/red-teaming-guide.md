# 🎯 Red Teaming Guide

Practical workflows for offensive security research using the local stack.

---

## ⚠️ Legal & Ethical Framework

This stack is designed for:
- ✅ Authorized penetration testing
- ✅ Defensive stress testing
- ✅ Vulnerability research on systems you own
- ✅ Security education and training
- ✅ Malware analysis in isolated environments

**Never use generated exploits against systems without explicit authorization.**

---

## Workflow 1: Threat Intelligence Analysis

**Scenario:** You have a collection of PDF reports, CVE advisories, and threat intel briefings.

### Step 1: Ingest Documents

1. Open http://localhost:8283/
2. Navigate to **Ingest** tab
3. Upload your threat intel folder (PDFs, TXTs, MDs)
4. Wait for "Ingested" status

### Step 2: Query Mode (The Auditor)

Use Query mode when you want **zero hallucination**:

```
"Summarize the attack vectors described in the APT29 report from 2024."
```

The model will ONLY answer using retrieved context. If the info is not in your documents, it will say so.

### Step 3: Chat Mode (The Analyst)

Use Chat mode when you want the model to **synthesize and extend**:

```
"Based on the TTPs described in the uploaded Mandiant report, 
generate a hypothetical detection rule in Sigma format for 
the lateral movement technique."
```

The model uses your documents as grounding but can apply its own knowledge to fill gaps.

---

## Workflow 2: Exploit Development

**Scenario:** You are analyzing a new vulnerability and need a PoC.

### Step 1: Ingest the Technical Paper

Upload the whitepaper, CVE details, and any proof-of-concept snippets.

### Step 2: Use the RedTeam Analyst Model

```bash
# Switch to the redteam-analyst personality
ollama run redteam-analyst
```

Or configure PrivateGPT to use it:
```yaml
ollama:
  llm_model: redteam-analyst
```

### Step 3: Generate the PoC

```
"The paper describes a use-after-free in the JPEG parser (Section 4.2). 
Generate a minimal C++ PoC that triggers this condition. 
Include comments explaining each step."
```

**Expected result:** The uncensored model generates working code with technical annotations. No refusals.

### Step 4: Iterate

```
"The PoC crashes but does not achieve code execution. 
Suggest modifications using the heap grooming technique 
mentioned in Figure 5 of the paper."
```

---

## Workflow 3: Log Analysis & Forensics

**Scenario:** You have server logs from an incident and need to reconstruct the timeline.

### Step 1: Ingest Logs

Upload log files (CSV, JSON, raw text). The embedding model will index them.

### Step 2: Timeline Reconstruction

```
"Find all events related to user 'admin' between 2024-01-15 and 2024-01-16. 
Present them in chronological order with timestamps."
```

### Step 3: IOC Extraction

```
"Extract all IP addresses, domains, and file hashes mentioned in the logs. 
Format as a structured JSON list."
```

### Step 4: Pattern Recognition

```
"Identify any anomalous login patterns. Look for:
- Failed login bursts
- Off-hours access
- Geographic anomalies
- Privilege escalation attempts"
```

---

## Workflow 4: Source Code Audit

**Scenario:** You need to review proprietary source code for vulnerabilities.

### Step 1: Ingest Source Code

Upload the codebase (or relevant modules). PrivateGPT handles large code files by chunking.

### Step 2: Targeted Queries

```
"Search the codebase for SQL query construction. 
Identify any locations where user input is concatenated directly into queries."
```

### Step 3: Vulnerability Classification

```
"For each potential SQL injection found, classify by:
- Severity (Critical/High/Medium/Low)
- Attack vector
- Recommended fix (parameterized query example)"
```

### Step 4: Generate Patch

```
"Generate a patch for the vulnerability in auth.py line 145. 
Use parameterized queries and input validation."
```

---

## Workflow 5: Automated Document Monitoring

**Scenario:** Your threat intel feed drops new files daily.

### Step 1: Configure the Watchdog

```bash
python3 tools/document-watchdog.py \
    --watch ~/threat-intel/incoming \
    --api http://localhost:8281 \
    --sensitivity-keywords "CVE,exploit,0day,APT,malware,shellcode"
```

### Step 2: Let It Run

The watchdog will:
- Detect new files in `~/threat-intel/incoming`
- Auto-ingest them into PrivateGPT
- Flag high-sensitivity documents
- Log everything to `watchdog.log`

### Step 3: Query the Fresh Intel

```
"What new CVEs were mentioned in documents ingested today?"
```

---

## 🛡️ OPSEC Checklist

Before each session:
- [ ] `host: 127.0.0.1` in settings (unless WSL bridge needed)
- [ ] No VPN leaks (check `curl ifconfig.me` from WSL)
- [ ] Documents ingested are from trusted sources
- [ ] Model weights verified (pull yourself, do not trust third-party images)
- [ ] Qdrant data directory is not synced to cloud storage
- [ ] Working directory is scoped (agent bridge cannot escape)

After each session:
- [ ] Clear conversation history if sensitive
- [ ] Verify no temporary files leaked outside working dir
- [ ] Rotate any test credentials used in prompts
