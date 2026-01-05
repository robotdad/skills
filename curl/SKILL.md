---
name: curl
description: "HTTP client for API testing, validation, and debugging. Use when tasks require: (1) Testing REST/GraphQL APIs, (2) Validating response status codes or bodies, (3) Debugging HTTP requests, (4) Sending webhooks, (5) Downloading files. Prefer curl over browser automation for backend API work."
license: MIT
---

# Curl HTTP Client

## Overview

Curl is the standard tool for HTTP requests from the command line. Use it for API testing, validation, and debugging. **Prefer curl over Playwright for any backend/API work** — it's faster, simpler, and has no browser overhead.

## Workflow Decision Tree

### Simple GET request or API test
→ Use "Basic Patterns" below

### Need authentication (tokens, API keys, OAuth)
→ Read [`patterns.md`](patterns.md) — "Authentication" section

### Uploading files or complex POST bodies
→ Read [`patterns.md`](patterns.md) — "Request Bodies" section

### Request failing or unexpected response
→ Read [`troubleshooting.md`](troubleshooting.md)

### Need to parse/validate JSON responses
→ Use "Response Handling with jq" below

## Basic Patterns

### GET request

```bash
curl https://api.example.com/users
```

### GET with headers

```bash
curl https://api.example.com/users \
  -H "Authorization: Bearer TOKEN" \
  -H "Accept: application/json"
```

### POST with JSON body

```bash
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John", "email": "john@example.com"}'
```

### PUT / PATCH / DELETE

```bash
# PUT - replace resource
curl -X PUT https://api.example.com/users/123 \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name"}'

# PATCH - partial update
curl -X PATCH https://api.example.com/users/123 \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name"}'

# DELETE
curl -X DELETE https://api.example.com/users/123
```

### Show response headers

```bash
# Headers + body
curl -i https://api.example.com/users

# Headers only
curl -I https://api.example.com/users
```

### Save response to file

```bash
curl -o response.json https://api.example.com/users
```

## Response Handling with jq

Install jq for JSON parsing: `apt-get install jq` or `brew install jq`

```bash
# Pretty print JSON
curl -s https://api.example.com/users | jq .

# Extract specific field
curl -s https://api.example.com/users/1 | jq '.name'

# Extract from array
curl -s https://api.example.com/users | jq '.[0].email'

# Filter array
curl -s https://api.example.com/users | jq '.[] | select(.active == true)'

# Extract multiple fields
curl -s https://api.example.com/users | jq '.[] | {name, email}'
```

## Validation Patterns

### Check status code

```bash
# Get status code only
status=$(curl -s -o /dev/null -w "%{http_code}" https://api.example.com/health)
echo "Status: $status"

# Assert status code
if [ "$status" -eq 200 ]; then
  echo "✓ API is healthy"
else
  echo "✗ API returned $status"
  exit 1
fi
```

### Validate response contains expected data

```bash
# Check if field exists and has expected value
response=$(curl -s https://api.example.com/users/1)
name=$(echo "$response" | jq -r '.name')

if [ "$name" = "expected_name" ]; then
  echo "✓ Name matches"
else
  echo "✗ Expected 'expected_name', got '$name'"
  exit 1
fi
```

### Check response time

```bash
curl -s -o /dev/null -w "Time: %{time_total}s\n" https://api.example.com/users
```

### Full request diagnostics

```bash
curl -s -o /dev/null -w "\
HTTP Code: %{http_code}\n\
Time Total: %{time_total}s\n\
Time Connect: %{time_connect}s\n\
Time TTFB: %{time_starttransfer}s\n\
Size: %{size_download} bytes\n" \
  https://api.example.com/users
```

## Essential Flags

| Flag | Purpose |
|------|---------|
| `-X METHOD` | HTTP method (GET, POST, PUT, DELETE, PATCH) |
| `-H "Header: Value"` | Add request header |
| `-d 'data'` | Request body (implies POST) |
| `-s` | Silent mode (no progress bar) |
| `-i` | Include response headers |
| `-I` | Headers only (HEAD request) |
| `-o file` | Save response to file |
| `-w "format"` | Custom output format |
| `-L` | Follow redirects |
| `-k` | Skip SSL verification (use cautiously) |
| `-v` | Verbose (debug) |
| `--fail` | Exit with error on HTTP errors (4xx/5xx) |

## Quick Reference

| Task | Command |
|------|---------|
| GET | `curl URL` |
| POST JSON | `curl -X POST -H "Content-Type: application/json" -d '{}' URL` |
| With auth | `curl -H "Authorization: Bearer TOKEN" URL` |
| Status only | `curl -s -o /dev/null -w "%{http_code}" URL` |
| Pretty JSON | `curl -s URL \| jq .` |
| Debug | `curl -v URL` |
| Follow redirects | `curl -L URL` |

## See Also

- [`patterns.md`](patterns.md) — Authentication, file uploads, GraphQL, cookies, retries
- [`troubleshooting.md`](troubleshooting.md) — Common errors, SSL issues, debugging
