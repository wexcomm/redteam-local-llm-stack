# MITRE ATT&ACK: Discovery (TA0007)

> Techniques to gain knowledge about the system and internal network.

---

## T1083: File and Directory Discovery

```bash
# Linux - find sensitive files
find / -type f \( -name "*.txt" -o -name "*.conf" -o -name "*.cfg" -o -name "*.ini" \) 2>/dev/null
find /home -type f -perm -4000 2>/dev/null
find /var/www -type f -name "*.php" 2>/dev/null | head -20

# Windows - search for sensitive files
dir /s /b C:\*.txt C:\*.conf C:\*.ini C:\*.xml 2>nul
Get-ChildItem -Path C:\ -Include *.txt,*.xml,*.conf -Recurse -ErrorAction SilentlyContinue
```

---

## T1082: System Information Discovery

```bash
# Linux
uname -a
cat /etc/os-release
cat /proc/version
lscpu
free -h
df -h
cat /etc/passwd
cat /etc/group

# Windows
systeminfo
wmic computersystem get name, domain, manufacturer, model
wmic os get caption, version, osarchitecture
wmic cpu get name, numberofcores, maxclockspeed
wmic logicaldisk get size, freespace, caption
```

---

## T1016: System Network Configuration Discovery

```bash
# Linux
ip addr
ip route
cat /etc/resolv.conf
netstat -tulpn
ss -tulpn
cat /etc/hosts

# Windows
ipconfig /all
route print
netstat -ano
Get-NetTCPConnection
Get-NetRoute
```

---

## T1049: System Network Connections Discovery

```bash
# Linux
netstat -tulpn
ss -tulpn
lsof -i
arp -a
cat /proc/net/tcp

# Windows
netstat -ano
Get-NetTCPConnection -State Established
Get-NetNeighbor
```

---

## T1018: Remote System Discovery

```bash
# Linux
nmap -sn 192.168.1.0/24
fping -a -g 192.168.1.0/24 2>/dev/null

# Windows
for /L %i in (1,1,254) do @ping -n 1 -w 100 192.168.1.%i | find "Reply"
1..254 | ForEach-Object { Test-Connection -Count 1 -TimeToLive 1 192.168.1.$_ -ErrorAction SilentlyContinue }
```

---

## T1069: Permission Groups Discovery

```bash
# Linux
groups
cat /etc/group
getent group admin sudo wheel
id

# Windows
whoami /groups
net localgroup
net group /domain
Get-ADGroup -Filter * | Select Name
```

---

## T1087: Account Discovery

```bash
# Linux
cat /etc/passwd
cat /etc/shadow (requires root)
getent passwd
who
w
last

# Windows
net user
net user /domain
net localgroup administrators
Get-ADUser -Filter * | Select Name, SamAccountName
```

---

## T1482: Domain Trust Discovery

```powershell
# PowerView
Get-NetDomainTrust
Get-NetForestTrust
Get-DomainTrustMapping

# nltest
nltest /domain_trusts
nltest /dclist:corp.com

# Active Directory
Get-ADTrust -Filter *
```

---

## T1135: Network Share Discovery

```bash
# Linux
showmount -e target
smbclient -L //target -N

# Windows
net view \\target
net view /domain:corp.com
Get-SmbShare -ComputerName target
Find-DomainShare -CheckShareAccess
```

---

## T1201: Password Policy Discovery

```bash
# Linux
cat /etc/login.defs
cat /etc/pam.d/common-password
chage -l username

# Windows
net accounts
net accounts /domain
Get-ADDefaultDomainPasswordPolicy
```

---

## T1033: System Owner/User Discovery

```bash
# Linux
echo $USER
echo $HOME
whoami
who
w
last

# Windows
whoami
whoami /user
whoami /groups
whoami /priv
$env:USERNAME
$env:USERDOMAIN
```

---

## T1124: System Time Discovery

```bash
# Linux
date
timedatectl

# Windows
time /t
date /t
wmic os get localdatetime
```

---

## Detection

| Technique | Detection |
|---|---|
| Network Scanning | IDS/IPS alerts, firewall logs, netflow anomalies |
| Domain Enumeration | Event ID 4661 (SAM handle request), 5136 (LDAP queries) |
| Share Enumeration | Event ID 5140 (network share accessed) |
| Permission Discovery | Event ID 4674 (privilege use) |
| Account Discovery | Event ID 4661, 4768 (Kerberos TGT request) |
