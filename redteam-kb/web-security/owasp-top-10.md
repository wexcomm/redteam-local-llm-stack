# OWASP Top 10 Web Application Security Risks

> The Open Web Application Security Project (OWASP) Top 10 is the industry standard for web application security awareness.

---

## A01:2021 – Broken Access Control

### Description
Access control enforces policy such that users cannot act outside their intended permissions. Failures typically lead to unauthorized information disclosure, modification, or destruction.

### Common Vulnerabilities
- Violation of least privilege
- Bypassing access control checks by modifying URL, HTML, or API requests
- Permitting viewing or editing someone else's account (IDOR)
- Elevation of privilege (acting as admin when logged in as user)
- Metadata manipulation (JWT, cookies, tokens)
- CORS misconfiguration

### Testing Methods
```bash
# IDOR testing - manipulate object references
curl -H "Cookie: session=abc123" https://app.com/api/orders/12345
curl -H "Cookie: session=abc123" https://app.com/api/orders/12346  # another user's order

# Horizontal privilege escalation
curl -H "Authorization: Bearer $TOKEN" https://app.com/api/users/1001/profile
curl -H "Authorization: Bearer $TOKEN" https://app.com/api/users/1002/profile  # try other IDs

# Vertical privilege escalation
curl -H "Cookie: session=user_session" https://app.com/admin/dashboard
```

### Prevention
- Deny by default
- Implement access control once and reuse
- Minimize CORS usage
- Rate limit API access
- Log access control failures

---

## A02:2021 – Cryptographic Failures

### Description
Failures related to cryptography that often lead to exposure of sensitive data.

### Common Issues
- Transmitting data in plaintext (HTTP, SMTP, FTP)
- Using outdated/weak cryptographic algorithms (MD5, SHA1, DES, RC4)
- Hardcoded cryptographic keys in source code
- Improper certificate validation
- Storing passwords using weak hashing (MD5, SHA1 without salt)

### Testing
```bash
# Check for weak TLS
testssl.sh https://target.com
nmap --script ssl-enum-ciphers -p 443 target.com

# Check for hardcoded keys
grep -ri "api_key\|secret_key\|password\|private_key" /var/www/
grep -ri "BEGIN RSA PRIVATE KEY" /var/www/
```

### Prevention
- Encrypt all data in transit (TLS 1.2+)
- Encrypt all data at rest
- Use strong, modern algorithms (AES-256-GCM, ChaCha20-Poly1305)
- Use Argon2id, bcrypt, or PBKDF2 for password hashing
- Proper key management (HSM, KMS)

---

## A03:2021 – Injection

### Description
Injection flaws occur when untrusted data is sent to an interpreter as part of a command or query.

### Types
- SQL Injection
- NoSQL Injection
- Command Injection
- LDAP Injection
- XPath Injection
- OS Command Injection
- Expression Language Injection (ELI/OGNL)

### Testing
Already covered in dedicated injection guide.

---

## A04:2021 – Insecure Design

- Missing security requirements in design phase
- Business logic flaws
- Missing threat modeling
- Trust boundaries not properly defined

---

## A05:2021 – Security Misconfiguration

### Common Issues
- Default accounts and passwords
- Unnecessary features enabled
- Error messages with stack traces
- Missing security headers
- Directory listing enabled
- Cloud storage misconfigurations (S3 buckets)

### Testing
```bash
# Check security headers
curl -I https://target.com | grep -iE "x-frame-options|x-xss-protection|content-security-policy|strict-transport-security|x-content-type-options"

# Check for directory listing
curl https://target.com/images/
curl https://target.com/backup/

# Check for default pages
curl https://target.com/phpinfo.php
curl https://target.com/.env
curl https://target.com/robots.txt

# Cloud storage enumeration
curl https://target.s3.amazonaws.com/
curl https://storage.googleapis.com/target-bucket/
```

---

## A06:2021 – Vulnerable and Outdated Components

- Known vulnerabilities in dependencies
- Unsupported/End-of-life software
- Missing patch management
- Software version not checked regularly

### Testing
```bash
# Dependency scanning
npm audit
pip-audit
snyk test

# Version detection
nmap -sV target.com
whatweb target.com
wappalyzer target.com
```

---

## A07:2021 – Identification and Authentication Failures

- Permitting automated attacks (credential stuffing, brute force)
- Weak password policies
- Missing or ineffective MFA
- Session fixation
- Session tokens exposed in URL
- Improper session invalidation

### Testing
```bash
# Password policy testing
curl -X POST https://target.com/api/login -d "username=admin&password=a"  # too short
curl -X POST https://target.com/api/login -d "username=admin&password=password123"  # common password

# Brute force
curl -X POST https://target.com/api/login -d "username=admin&password=123456"
curl -X POST https://target.com/api/login -d "username=admin&password=password"
```

---

## A08:2021 – Software and Data Integrity Failures

- Insecure deserialization
- Unsigned/unchecked updates
- CI/CD pipeline compromise
- Dependency confusion

### Deserialization Testing
```bash
# Java deserialization
curl -X POST https://target.com/api/process -H "Content-Type: application/x-java-serialized-object" --data-binary @payload.ser

# PHP deserialization
curl -X POST https://target.com/api/process -d "data=O:8:"stdClass":1:{s:4:"test";s:4:"test";};"
```

---

## A09:2021 – Security Logging and Monitoring Failures

- Insufficient logging
- Logs not monitored
- Logs stored locally only
- No incident response plan

---

## A10:2021 – Server-Side Request Forgery (SSRF)

### Description
SSRF occurs when a web application fetches a remote resource without validating the user-supplied URL.

### Testing
```bash
# Basic SSRF
curl -X POST https://target.com/api/fetch -d "url=http://169.254.169.254/latest/meta-data/iam/security-credentials/"

# DNS rebinding
curl -X POST https://target.com/api/fetch -d "url=http://attacker-controlled-domain.com"

# Internal port scanning
curl -X POST https://target.com/api/fetch -d "url=http://127.0.0.1:22"  # SSH
curl -X POST https://target.com/api/fetch -d "url=http://127.0.0.1:3306"  # MySQL
curl -X POST https://target.com/api/fetch -d "url=http://127.0.0.1:6379"  # Redis

# Gopher protocol abuse
curl -X POST https://target.com/api/fetch -d "url=gopher://127.0.0.1:6379/_FLUSHALL"
```

### Prevention
- URL validation and whitelisting
- Disable unnecessary URL schemas
- Network segmentation
- Enforce authentication on internal services
