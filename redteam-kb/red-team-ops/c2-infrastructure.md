# C2 Infrastructure Guide

> Building resilient command and control infrastructure.

---

## C2 Frameworks

| Framework | Language | Features | Use Case |
|---|---|---|---|
| Cobalt Strike | Java | Malleable C2, pivoting, post-exploitation | Enterprise red team |
| Sliver | Go | Multiplayer, DNS/HTTP/HTTPS C2, implants | Modern alternative to CS |
| Mythic | Python/Go | Docker-based, custom agents | Flexible C2 |
| Metasploit | Ruby | Extensive exploit library | General purpose |
| Havoc | C | Modern design, sleep obfuscation | Stealth operations |
| Brute Ratel | C | EDR evasion, sleep obfuscation | Advanced evasion |
| PoshC2 | Python | PowerShell focused | Windows environments |
| Covenant | C# | .NET focused, reflective execution | Windows environments |

---

## C2 Communication Channels

### HTTP/HTTPS
- Most common
- Blends with normal traffic
- Malleable C2 profiles

### DNS
- DNS tunneling for covert channels
- Slow but stealthy
- Tools: dnscat2, iodine, dns2tcp

### SMB
- Named pipes
- Works in segmented networks
- Tools: Cobalt Strike SMB beacon

### TCP/UDP Direct
- Fast and reliable
- More visible to IDS

### ICMP
- Often allowed through firewalls
- Tools: icmpsh, ptunnel

### Cloud Services
- Slack, Discord, Telegram bots
- GitHub Issues, Gists
- Twitter, Reddit
- OneDrive, Google Drive

---

## Malleable C2 Profile (Cobalt Strike Example)

```
http-get {
    set uri "/api/v1/updates";
    client {
        header "Accept" "application/json";
        header "User-Agent" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)";
        metadata {
            base64url;
            prepend "session=";
            header "Cookie";
        }
    }
    server {
        header "Content-Type" "application/json";
        output {
            base64;
            print;
        }
    }
}
```

---

## Sleep Obfuscation

- Encrypt beacon in memory during sleep
- Unmap from memory
- Use legitimate thread pool waits
- Tools: Foliage, Ekko, ShellcodeFluctuation

---

## Redirector Setup

```bash
# DigitalOcean/Linode VPS as redirector
# Nginx reverse proxy

server {
    listen 443 ssl;
    server_name updates.microsoft-cdn.com;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    location /api/v1/updates {
        proxy_pass http://c2-backend:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
