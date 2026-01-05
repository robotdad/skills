# Curl Troubleshooting

## Diagnostic First Steps

When a request fails, get verbose output:

```bash
curl -v https://api.example.com/endpoint
```

This shows:
- DNS resolution
- TCP connection
- TLS handshake
- Request headers sent
- Response headers received

### Isolate the problem

```bash
# 1. Can you reach the host at all?
ping api.example.com

# 2. Is the port open?
nc -zv api.example.com 443

# 3. Does DNS resolve?
nslookup api.example.com

# 4. Is it a TLS issue?
openssl s_client -connect api.example.com:443

# 5. Is it a curl-specific issue?
wget https://api.example.com/endpoint  # Try alternative
```

## Common Errors & Solutions

### "curl: (6) Could not resolve host"

**Cause:** DNS resolution failed.

```bash
# Check DNS
nslookup api.example.com
dig api.example.com

# Try with explicit DNS server
curl --dns-servers 8.8.8.8 https://api.example.com/endpoint

# Check /etc/resolv.conf
cat /etc/resolv.conf

# Possible fixes:
# - Check hostname spelling
# - Try IP address directly
# - Check network connectivity
# - Flush DNS cache
```

### "curl: (7) Failed to connect to host"

**Cause:** TCP connection failed (host unreachable, port closed, firewall).

```bash
# Test port connectivity
nc -zv api.example.com 443
telnet api.example.com 443

# Check if firewall is blocking
sudo iptables -L -n

# Try from different network/VPN
# Check if service is actually running
```

### "curl: (28) Operation timed out"

**Cause:** Server didn't respond in time.

```bash
# Increase timeout
curl --connect-timeout 30 --max-time 120 https://api.example.com/slow

# Check if it's connect or response timeout
curl -v --connect-timeout 5 https://api.example.com/endpoint

# Possible causes:
# - Server overloaded
# - Network latency
# - Firewall silently dropping packets
# - Wrong port
```

### "curl: (35) SSL connect error" / TLS errors

**Cause:** TLS handshake failed.

```bash
# Check certificate details
openssl s_client -connect api.example.com:443

# Try different TLS version
curl --tlsv1.2 https://api.example.com/endpoint
curl --tlsv1.3 https://api.example.com/endpoint

# Skip verification (TESTING ONLY)
curl -k https://api.example.com/endpoint

# Common causes:
# - Expired certificate
# - Self-signed certificate
# - Wrong hostname in certificate
# - Outdated curl/OpenSSL
# - Missing intermediate certificates
```

### "curl: (51) SSL: certificate subject name does not match"

**Cause:** Hostname doesn't match certificate.

```bash
# Check certificate's valid names
openssl s_client -connect api.example.com:443 | openssl x509 -noout -text | grep -A1 "Subject Alternative Name"

# Use correct hostname
curl https://correct-hostname.example.com/endpoint

# Skip verification (TESTING ONLY)
curl -k https://api.example.com/endpoint
```

### "curl: (52) Empty reply from server"

**Cause:** Server closed connection without sending anything.

```bash
# Might be wrong protocol (HTTP vs HTTPS)
curl http://api.example.com/endpoint   # Try HTTP
curl https://api.example.com/endpoint  # Try HTTPS

# Might be server-side error - check with verbose
curl -v https://api.example.com/endpoint

# Could be WAF/proxy blocking the request
# Try different User-Agent
curl -A "Mozilla/5.0" https://api.example.com/endpoint
```

### "curl: (56) Recv failure: Connection reset by peer"

**Cause:** Server abruptly closed connection.

```bash
# Could be:
# - Server crashed
# - Firewall/WAF blocking
# - Request too large
# - Keep-alive timeout

# Try without keep-alive
curl -H "Connection: close" https://api.example.com/endpoint

# Try smaller request
# Check server logs if you have access
```

### HTTP 4xx Errors

```bash
# 400 Bad Request - Check request format
curl -v -X POST https://api.example.com/endpoint \
  -H "Content-Type: application/json" \
  -d '{"valid": "json"}'

# 401 Unauthorized - Check authentication
curl -H "Authorization: Bearer CHECK_TOKEN" https://api.example.com/endpoint

# 403 Forbidden - Check permissions, IP restrictions, CORS
# Try with browser User-Agent
curl -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0" \
  https://api.example.com/endpoint

# 404 Not Found - Check URL path
curl -v https://api.example.com/correct/path

# 405 Method Not Allowed - Check HTTP method
curl -X GET https://api.example.com/endpoint  # Try different method

# 429 Too Many Requests - Rate limited
# Wait and retry, or check rate limit headers
curl -i https://api.example.com/endpoint | grep -i "rate\|retry"
```

### HTTP 5xx Errors

```bash
# 500 Internal Server Error - Server-side problem
# Retry later, check if your request is malformed

# 502 Bad Gateway - Upstream server issue
# Usually transient, retry

# 503 Service Unavailable - Server overloaded/maintenance
# Check Retry-After header
curl -i https://api.example.com/endpoint | grep -i retry-after

# 504 Gateway Timeout - Upstream timeout
# Request may be too slow, try simpler query
```

## Debugging Techniques

### Verbose output

```bash
curl -v https://api.example.com/endpoint
```

### Extra verbose (includes data)

```bash
curl -v --trace-ascii debug.txt https://api.example.com/endpoint
cat debug.txt
```

### See what curl would send (without sending)

```bash
curl -v --dry-run https://api.example.com/endpoint 2>&1 | grep "^>"
```

### Time breakdown

```bash
curl -w "\
DNS Lookup:    %{time_namelookup}s\n\
TCP Connect:   %{time_connect}s\n\
TLS Handshake: %{time_appconnect}s\n\
First Byte:    %{time_starttransfer}s\n\
Total Time:    %{time_total}s\n\
" -o /dev/null -s https://api.example.com/endpoint
```

### Compare with browser request

1. Open browser DevTools → Network tab
2. Make the request
3. Right-click → Copy as cURL
4. Compare with your curl command

### Test from different environment

```bash
# From Docker container
docker run --rm curlimages/curl https://api.example.com/endpoint

# From different server
ssh other-server "curl https://api.example.com/endpoint"
```

## JSON Issues

### "parse error: Invalid numeric literal"

**Cause:** Response is not valid JSON, or using jq on non-JSON.

```bash
# Check raw response first
curl -s https://api.example.com/endpoint

# Is it HTML error page?
curl -s https://api.example.com/endpoint | head

# Check content type
curl -sI https://api.example.com/endpoint | grep content-type
```

### Escaping JSON in shell

```bash
# Use single quotes for JSON
curl -d '{"name": "John"}' ...

# Or escape double quotes
curl -d "{\"name\": \"John\"}" ...

# Or use heredoc for complex JSON
curl -X POST https://api.example.com/endpoint \
  -H "Content-Type: application/json" \
  -d @- << 'EOF'
{
  "name": "John",
  "items": ["a", "b", "c"]
}
EOF

# Or read from file
echo '{"name": "John"}' > payload.json
curl -d @payload.json ...
```

## Authentication Issues

### Token validation

```bash
# Check if token is expired (JWT)
echo "YOUR_JWT_TOKEN" | cut -d'.' -f2 | base64 -d 2>/dev/null | jq '.exp | todate'

# Check token format
echo "YOUR_TOKEN" | head -c 50  # See first 50 chars
```

### Common auth mistakes

```bash
# Wrong: Space after Bearer
curl -H "Authorization: Bearer  TOKEN" ...

# Wrong: Token has newline
TOKEN="abc123
"  # Hidden newline
curl -H "Authorization: Bearer $TOKEN" ...

# Right: Trim whitespace
TOKEN=$(echo "$TOKEN" | tr -d '\n\r ')
curl -H "Authorization: Bearer $TOKEN" ...
```

## SSL/TLS Certificate Issues

### View certificate chain

```bash
openssl s_client -connect api.example.com:443 -showcerts
```

### Check certificate expiry

```bash
echo | openssl s_client -connect api.example.com:443 2>/dev/null | \
  openssl x509 -noout -dates
```

### Use specific CA bundle

```bash
curl --cacert /path/to/ca-bundle.crt https://api.example.com/endpoint
```

### Update CA certificates

```bash
# Debian/Ubuntu
sudo apt-get update && sudo apt-get install ca-certificates
sudo update-ca-certificates

# macOS
brew install ca-certificates
```

## Encoding Issues

### URL encode parameters

```bash
# Use --data-urlencode for form data
curl -G https://api.example.com/search \
  --data-urlencode "query=hello world" \
  --data-urlencode "filter=name:John Doe"
```

### Handle special characters in JSON

```bash
# Use jq to build JSON safely
name="O'Brien"
email="test+special@example.com"

curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg name "$name" --arg email "$email" \
    '{name: $name, email: $email}')"
```

## Quick Diagnostic Checklist

1. **Can you reach the host?** → `ping`, `nc -zv`
2. **DNS working?** → `nslookup`, `dig`
3. **TLS working?** → `openssl s_client`
4. **What does verbose show?** → `curl -v`
5. **What status code?** → `curl -w "%{http_code}"`
6. **What's the actual response?** → `curl -s URL | head`
7. **Works from browser?** → Copy as cURL, compare
8. **Works from different machine?** → Test from container/other server
