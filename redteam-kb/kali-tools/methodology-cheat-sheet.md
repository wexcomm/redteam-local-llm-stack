# Penetration Testing Methodology Cheat Sheet

> Structured workflow for penetration testing engagements.

---

## Pre-Engagement

1. **Scope Definition**
   - IP ranges, domains, applications
   - Exclusions and restrictions
   - Testing windows and times
   - Emergency contacts

2. **Rules of Engagement**
   - Authorized techniques
   - Data handling requirements
   - Reporting requirements
   - Communication protocols

3. **Legal Documentation**
   - Signed authorization letter
   - NDA agreements
   - Insurance verification

---

## Phase 1: Reconnaissance

### Passive Recon
- [ ] WHOIS lookup
- [ ] DNS enumeration (subdomains, MX, TXT)
- [ ] Certificate transparency logs
- [ ] Search engine dorking (Google, Bing, Shodan)
- [ ] Social media analysis
- [ ] GitHub/GitLab repository search
- [ ] Wayback Machine
- [ ] Public breach databases

### Active Recon
- [ ] Host discovery (ping sweep)
- [ ] Port scanning (TCP/UDP)
- [ ] Service enumeration
- [ ] OS fingerprinting
- [ ] Web technology detection

---

## Phase 2: Vulnerability Analysis

### Web Applications
- [ ] Spider/crawl application
- [ ] Directory/file brute force
- [ ] Parameter fuzzing
- [ ] Authentication testing
- [ ] Session management testing
- [ ] Input validation testing (XSS, SQLi, XXE, etc.)
- [ ] Business logic testing
- [ ] API testing
- [ ] File upload testing

### Network Services
- [ ] Default credentials
- [ ] Service-specific vulnerabilities
- [ ] Misconfigurations
- [ ] Information disclosure
- [ ] Encryption weaknesses

### Infrastructure
- [ ] Patch levels
- [ ] Configuration review
- [ ] Segmentation testing
- [ ] Cloud configuration review

---

## Phase 3: Exploitation

### Initial Access
- [ ] Exploit public-facing application
- [ ] Phishing campaign (if authorized)
- [ ] Credential-based access
- [ ] Physical access (if authorized)

### Post-Exploitation Checklist
- [ ] **System Enumeration**
  - OS version and patch level
  - User accounts and privileges
  - Network configuration
  - Running processes
  - Installed software
  - Scheduled tasks/cron jobs

- [ ] **Privilege Escalation**
  - Kernel exploits
  - Service misconfigurations
  - SUID/SUDO abuse
  - Token abuse (Windows)
  - Credential harvesting

- [ ] **Persistence**
  - Registry keys (Windows)
  - Scheduled tasks/cron
  - Services
  - Web shells
  - Startup items

- [ ] **Credential Harvesting**
  - Password hashes
  - Kerberos tickets
  - Browser credentials
  - SSH keys
  - Cloud credentials

- [ ] **Lateral Movement**
  - Pass-the-hash
  - Pass-the-ticket
  - RDP
  - SMB/PSExec
  - WinRM
  - SSH

- [ ] **Data Collection**
  - Sensitive file discovery
  - Database dumps
  - Email collection
  - Configuration files

---

## Phase 4: Reporting

### Executive Summary
- High-level findings
- Risk ratings
- Business impact
- Remediation priorities

### Technical Findings
- Vulnerability details
- Proof of concept
- Screenshots/evidence
- Affected systems
- CVSS scores

### Remediation
- Specific fixes
- Configuration changes
- Patch recommendations
- Compensating controls

### Appendices
- Scope and methodology
- Tool outputs
- Raw data
- Glossary

---

## CVSS Scoring Guide

| Score | Severity | Color |
|-------|----------|-------|
| 0.0 | None | ⚪ |
| 0.1-3.9 | Low | 🟢 |
| 4.0-6.9 | Medium | 🟡 |
| 7.0-8.9 | High | 🟠 |
| 9.0-10.0 | Critical | 🔴 |
