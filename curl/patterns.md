# Curl Advanced Patterns

## Authentication

### Bearer token (JWT, OAuth)

```bash
curl https://api.example.com/protected \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

### API key (header)

```bash
curl https://api.example.com/data \
  -H "X-API-Key: your-api-key"
```

### API key (query parameter)

```bash
curl "https://api.example.com/data?api_key=your-api-key"
```

### Basic auth

```bash
# Inline credentials
curl -u username:password https://api.example.com/data

# Prompt for password
curl -u username https://api.example.com/data

# Explicit header (base64 encoded username:password)
curl -H "Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=" https://api.example.com/data
```

### OAuth 2.0 token flow

```bash
# Get token
response=$(curl -s -X POST https://auth.example.com/oauth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET")

token=$(echo "$response" | jq -r '.access_token')

# Use token
curl https://api.example.com/data \
  -H "Authorization: Bearer $token"
```

### AWS Signature v4 (using --aws-sigv4)

```bash
curl --aws-sigv4 "aws:amz:us-east-1:execute-api" \
  --user "$AWS_ACCESS_KEY_ID:$AWS_SECRET_ACCESS_KEY" \
  https://api-id.execute-api.us-east-1.amazonaws.com/stage/resource
```

## Request Bodies

### JSON body

```bash
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John", "email": "john@example.com"}'
```

### JSON from file

```bash
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d @payload.json
```

### Form data (application/x-www-form-urlencoded)

```bash
curl -X POST https://api.example.com/login \
  -d "username=john" \
  -d "password=secret"

# Or combined
curl -X POST https://api.example.com/login \
  -d "username=john&password=secret"
```

### Multipart form (file upload)

```bash
# Single file
curl -X POST https://api.example.com/upload \
  -F "file=@document.pdf"

# File with custom filename
curl -X POST https://api.example.com/upload \
  -F "file=@document.pdf;filename=report.pdf"

# File with explicit content type
curl -X POST https://api.example.com/upload \
  -F "file=@image.png;type=image/png"

# Multiple files
curl -X POST https://api.example.com/upload \
  -F "files=@file1.pdf" \
  -F "files=@file2.pdf"

# File + additional fields
curl -X POST https://api.example.com/upload \
  -F "file=@document.pdf" \
  -F "description=Quarterly Report" \
  -F "folder_id=123"
```

### Binary data

```bash
curl -X POST https://api.example.com/upload \
  -H "Content-Type: application/octet-stream" \
  --data-binary @image.png
```

## GraphQL

### Query

```bash
curl -X POST https://api.example.com/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { users { id name email } }"
  }'
```

### Query with variables

```bash
curl -X POST https://api.example.com/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query GetUser($id: ID!) { user(id: $id) { name email } }",
    "variables": {"id": "123"}
  }'
```

### Mutation

```bash
curl -X POST https://api.example.com/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "query": "mutation CreateUser($input: CreateUserInput!) { createUser(input: $input) { id name } }",
    "variables": {"input": {"name": "John", "email": "john@example.com"}}
  }'
```

## Cookies

### Send cookies

```bash
curl -b "session_id=abc123; csrf_token=xyz789" https://api.example.com/data
```

### Send cookies from file

```bash
curl -b cookies.txt https://api.example.com/data
```

### Save cookies from response

```bash
curl -c cookies.txt https://api.example.com/login \
  -d "username=john&password=secret"
```

### Full session (save + send)

```bash
# Login and save cookies
curl -c cookies.txt -X POST https://api.example.com/login \
  -d "username=john&password=secret"

# Use saved cookies for subsequent requests
curl -b cookies.txt https://api.example.com/protected-resource
```

## Timeouts & Retries

### Set timeouts

```bash
curl --connect-timeout 5 \  # Connection timeout (seconds)
     --max-time 30 \        # Total operation timeout
     https://api.example.com/slow-endpoint
```

### Retry on failure

```bash
curl --retry 3 \           # Retry up to 3 times
     --retry-delay 2 \     # Wait 2 seconds between retries
     --retry-max-time 60 \ # Max total retry time
     https://api.example.com/flaky-endpoint

# Retry on specific HTTP codes
curl --retry 3 --retry-all-errors https://api.example.com/endpoint
```

### Retry with exponential backoff (script)

```bash
max_attempts=5
attempt=1
delay=1

while [ $attempt -le $max_attempts ]; do
  response=$(curl -s -w "\n%{http_code}" https://api.example.com/endpoint)
  status=$(echo "$response" | tail -n1)
  body=$(echo "$response" | sed '$d')
  
  if [ "$status" -eq 200 ]; then
    echo "$body"
    exit 0
  fi
  
  echo "Attempt $attempt failed (status $status), retrying in ${delay}s..."
  sleep $delay
  attempt=$((attempt + 1))
  delay=$((delay * 2))
done

echo "All attempts failed"
exit 1
```

## Redirects

### Follow redirects

```bash
curl -L https://example.com/redirect-me
```

### Limit redirect depth

```bash
curl -L --max-redirs 5 https://example.com/redirect-chain
```

### Show redirect path

```bash
curl -L -w "Redirects: %{num_redirects}\nFinal URL: %{url_effective}\n" \
  -o /dev/null -s https://example.com/redirect-me
```

## Download Files

### Simple download

```bash
curl -O https://example.com/file.zip  # Save as file.zip (remote name)
curl -o local.zip https://example.com/file.zip  # Custom name
```

### Resume interrupted download

```bash
curl -C - -O https://example.com/large-file.zip
```

### Download with progress bar

```bash
curl -# -O https://example.com/file.zip
```

### Download only if modified

```bash
curl -z "2024-01-01" https://example.com/file.json -o file.json
```

## Parallel Requests

### Using xargs

```bash
echo "https://api.example.com/users/1
https://api.example.com/users/2
https://api.example.com/users/3" | xargs -P 3 -I {} curl -s {}
```

### Using GNU parallel

```bash
cat urls.txt | parallel -j 5 curl -s {}
```

### Background jobs

```bash
curl -s https://api.example.com/endpoint1 > result1.json &
curl -s https://api.example.com/endpoint2 > result2.json &
curl -s https://api.example.com/endpoint3 > result3.json &
wait
echo "All requests completed"
```

## Proxy Configuration

### HTTP proxy

```bash
curl -x http://proxy.example.com:8080 https://api.example.com/data
```

### SOCKS proxy

```bash
curl --socks5 localhost:9050 https://api.example.com/data
```

### Proxy with auth

```bash
curl -x http://user:password@proxy.example.com:8080 https://api.example.com/data
```

## Request Customization

### Custom method

```bash
curl -X CUSTOM_METHOD https://api.example.com/resource
```

### HTTP/2

```bash
curl --http2 https://api.example.com/data
```

### Compressed response

```bash
curl --compressed https://api.example.com/data
```

### Custom User-Agent

```bash
curl -A "MyApp/1.0" https://api.example.com/data
```

### Disable SSL verification (testing only)

```bash
curl -k https://self-signed.example.com/data
```

### Client certificate

```bash
curl --cert client.pem --key client-key.pem https://mtls.example.com/data
```
