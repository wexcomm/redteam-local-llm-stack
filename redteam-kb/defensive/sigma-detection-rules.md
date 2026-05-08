# Sigma Detection Rules Guide

> Sigma is a generic signature format for SIEM systems.

---

## Sigma Rule Structure

```yaml
title: Suspicious PowerShell Download
status: experimental
description: Detects suspicious PowerShell download cradle
logsource:
    product: windows
    service: powershell
detection:
    selection:
        EventID: 4104
        ScriptBlockText|contains:
            - 'IEX (New-Object Net.WebClient).DownloadString'
            - 'Invoke-Expression'
            - 'bitsadmin /transfer'
            - 'certutil -urlcache -split -f'
    condition: selection
falsepositives:
    - Administrative scripts
level: high
tags:
    - attack.execution
    - attack.t1059.001
```

---

## Common Detection Rules

### PowerShell Abuse
```yaml
title: PowerShell Encoded Command
description: Detects encoded PowerShell commands
logsource:
    product: windows
    service: powershell
detection:
    selection:
        EventID: 4104
        ScriptBlockText|contains:
            - '-enc '
            - '-encodedcommand '
            - '-e '
    condition: selection
level: medium
```

### LSASS Access
```yaml
title: LSASS Memory Access
description: Detects access to LSASS process
detection:
    selection:
        EventID: 10
        TargetImage|endswith: '\lsass.exe'
        GrantedAccess|contains:
            - '0x1010'
            - '0x1410'
            - '0x143a'
            - '0x1438'
    condition: selection
level: high
```

### Mimikatz Usage
```yaml
title: Mimikatz Indicators
description: Detects Mimikatz execution
detection:
    selection:
        - CommandLine|contains:
            - 'sekurlsa::'
            - 'kerberos::'
            - 'lsadump::'
            - 'token::'
        - Image|endswith: '\mimikatz.exe'
    condition: selection
level: critical
```

### DCSync Attack
```yaml
title: DCSync Attack
description: Detects AD replication from non-DC
detection:
    selection:
        EventID: 4662
        Properties|contains:
            - 'Replicating Directory Changes'
            - 'Replicating Directory Changes All'
    filter:
        SubjectUserName|endswith: '$'
    condition: selection and not filter
level: high
```

### Unquoted Service Path
```yaml
title: Service Installation with Unquoted Path
detection:
    selection:
        EventID: 7045
        ImagePath|re: '^[A-Z]:\[^"]*\[^"]*\[^"]*\.exe'
    condition: selection
level: medium
```

---

## Conversion Tools

```bash
# Convert to Splunk
sigmac -t splunk rule.yml

# Convert to Elastic
sigmac -t es-qs rule.yml

# Convert to Kibana
sigmac -t kibana rule.yml

# Convert to Sentinel
sigmac -t azure rule.yml

# Convert to Chronicle
sigmac -t chronicle rule.yml
```
