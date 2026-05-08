# Incident Response Playbook

> Structured response procedures for common attack scenarios.

---

## Incident Response Phases

### 1. Preparation
- [ ] IR policy and procedures documented
- [ ] IR team roles defined
- [ ] Communication plans established
- [ ] Toolkits prepared
- [ ] Training completed
- [ ] Playbooks developed

### 2. Detection & Analysis
- [ ] Alert triage
- [ ] Scope determination
- [ ] Evidence collection
- [ ] Timeline creation
- [ ] Threat intelligence correlation

### 3. Containment
- [ ] Short-term containment (isolate affected systems)
- [ ] Long-term containment (patch, config changes)
- [ ] Evidence preservation

### 4. Eradication
- [ ] Remove malware
- [ ] Close vulnerabilities
- [ ] Reset credentials
- [ ] Remove persistence

### 5. Recovery
- [ ] Restore from clean backups
- [ ] Validate systems
- [ ] Monitor for re-infection
- [ ] Return to normal operations

### 6. Lessons Learned
- [ ] Post-incident review
- [ ] Documentation updates
- [ ] Control improvements
- [ ] Training updates

---

## Response Procedures by Attack Type

### Ransomware
1. Isolate affected systems immediately
2. Identify ransomware variant (ID Ransomware, Any.Run)
3. Check for decryptor availability (NoMoreRansom)
4. Preserve evidence before cleanup
5. Restore from clean backups
6. DO NOT PAY RANSOM (no guarantee of recovery)

### Data Breach
1. Identify data accessed/exfiltrated
2. Determine legal/regulatory notification requirements
3. Preserve logs and evidence
4. Contain access
5. Notify affected parties per regulations (GDPR, CCPA, etc.)
6. Implement compensating controls

### Lateral Movement
1. Identify source of compromise
2. Map affected systems
3. Isolate compromised accounts
4. Reset credentials for all potentially affected accounts
5. Review privileged access
6. Check for persistence mechanisms

### Phishing Campaign
1. Identify affected users
2. Reset credentials for affected accounts
3. Check for mailbox rules (email forwarding)
4. Scan for malware on affected endpoints
5. Remove phishing emails from all mailboxes
6. User awareness training

---

## Evidence Collection

### Windows
```powershell
# Memory dump
.
winpmem_mini_x64.exe memory.raw

# Event logs
wevtutil epl Security C:\temp\security.evtx
wevtutil epl System C:\temp\system.evtx
wevtutil epl Application C:\temp\application.evtx
wevtutil epl "Microsoft-Windows-PowerShell/Operational" C:\temp\powershell.evtx
wevtutil epl "Microsoft-Windows-Sysmon/Operational" C:\temp\sysmon.evtx

# Registry
reg save HKLM\SAM C:\temp\sam.hive
reg save HKLM\SYSTEM C:\temp\system.hive
reg save HKLM\SECURITY C:\temp\security.hive

# Prefetch
Get-ChildItem C:\Windows\Prefetch | Compress-Archive -DestinationPath C:\temp\prefetch.zip

# MFT
.
RawCopy.exe /FileNamePath:C:\$MFT /OutputPath:C:\temp\
```

### Linux
```bash
# Memory
sudo dd if=/dev/mem of=/tmp/memory.raw bs=1M

# Logs
sudo tar -czvf /tmp/logs.tar.gz /var/log/
sudo cp /var/log/auth.log /tmp/
sudo cp /var/log/syslog /tmp/

# Bash history
cp ~/.bash_history /tmp/
cp /home/*/.bash_history /tmp/ 2>/dev/null

# Running processes
ps aux > /tmp/processes.txt
lsof > /tmp/open_files.txt
netstat -tulpn > /tmp/network.txt
ss -tulpn > /tmp/network2.txt

# Cron jobs
crontab -l > /tmp/cron.txt
sudo cat /etc/crontab > /tmp/system_crontab.txt
sudo ls -la /etc/cron.* > /tmp/cron_dirs.txt
```

---

## Forensic Analysis Commands

### Windows
```powershell
# Timeline analysis
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4624,4625,4648,4672} | Select TimeCreated, Id, LevelDisplayName, Message

# File timeline
Get-ChildItem -Path C:\ -Recurse -ErrorAction SilentlyContinue | Select FullName, LastWriteTime, LastAccessTime, CreationTime | Sort LastWriteTime -Descending

# Recently created files
Get-ChildItem -Path C:\Windows\Temp, C:\Users -Recurse -ErrorAction SilentlyContinue | Where-Object {$_.CreationTime -gt (Get-Date).AddDays(-7)} | Select FullName, CreationTime
```

### Linux
```bash
# File timeline
find / -type f -mtime -7 -ls 2>/dev/null
find / -type f -newermt "2024-01-01" ! -newermt "2024-01-02" -ls 2>/dev/null

# Recently modified files
find / -type f -mmin -60 -ls 2>/dev/null

# Deleted files (from /proc)
ls -la /proc/*/fd/ | grep deleted
```
