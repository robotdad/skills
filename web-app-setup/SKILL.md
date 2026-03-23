---
name: web-app-setup
description: Use when setting up a new web app on a Linux host — provisions shared infra gaps and per-app config. Always run host-infra-discovery first and have its summary table ready before starting.
---

# Web App Setup

## Overview

Takes the summary table from `host-infra-discovery` and does the work. Two phases: fix shared infra gaps (same for every app, idempotent), then provision per-app config (always done fresh).

Prefix every command with `ssh <hostname>` for remote hosts.

---

## Phase 1 — Shared Infra (Idempotent, Driven by Discovery Output)

Work through each row in the discovery table. Skip any row already showing the target state.

### Caddy not installed

```bash
apt-get update -qq && apt-get install -y caddy
systemctl enable --now caddy
```

### Caddy conf.d not wired

```bash
mkdir -p /etc/caddy/conf.d
grep -q 'import.*conf.d' /etc/caddy/Caddyfile || \
    echo 'import /etc/caddy/conf.d/*.caddy' | tee -a /etc/caddy/Caddyfile
```

### TLS certs absent (requires paid Tailscale plan)

```bash
FQDN=$(tailscale status --json | python3 -c \
    "import sys,json; print(json.load(sys.stdin)['Self']['DNSName'].rstrip('.'))")
mkdir -p /etc/ssl/tailscale
tailscale cert \
    --cert-file /etc/ssl/tailscale/$FQDN.crt \
    --key-file  /etc/ssl/tailscale/$FQDN.key \
    "$FQDN"
chown root:caddy /etc/ssl/tailscale/$FQDN.key
chmod 640        /etc/ssl/tailscale/$FQDN.key
```

On failure (free plan): set `HTTPS=false` and use port 80 with no `tls` directive in the Caddy snippet (Phase 2). Tailscale WireGuard still encrypts the connection.

### Cert renewal timer absent

```bash
# Write the two unit files
cat > /etc/systemd/system/tailscale-cert-renew.service <<'EOF'
[Unit]
Description=Renew Tailscale TLS certificates

[Service]
Type=oneshot
ExecStart=/usr/bin/tailscale cert \
    --cert-file /etc/ssl/tailscale/FQDN.crt \
    --key-file  /etc/ssl/tailscale/FQDN.key \
    FQDN
ExecStartPost=/usr/bin/chown root:caddy /etc/ssl/tailscale/FQDN.key
ExecStartPost=/usr/bin/chmod 640 /etc/ssl/tailscale/FQDN.key
ExecStartPost=/usr/bin/systemctl reload caddy
EOF

# Substitute actual FQDN
sed -i "s/FQDN/$FQDN/g" /etc/systemd/system/tailscale-cert-renew.service

cat > /etc/systemd/system/tailscale-cert-renew.timer <<'EOF'
[Unit]
Description=Weekly Tailscale cert renewal

[Timer]
OnCalendar=weekly
Persistent=true

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload
systemctl enable --now tailscale-cert-renew.timer
```

### Service user not in shadow group

```bash
usermod -aG shadow <SERVICE_USER>
```

---

## Phase 2 — Per-App (Always Run These)

Replace `<APPNAME>` with a short lowercase slug (e.g. `filebrowser`, `myapp`).

### 2a. Generate secret key

```bash
INSTALL_DIR="/opt/<APPNAME>"
mkdir -p "$INSTALL_DIR"

SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
echo "$SECRET" > "$INSTALL_DIR/.secret_key"
chmod 600 "$INSTALL_DIR/.secret_key"
```

### 2b. Allocate port

Find the next free port not already in `/etc/app-ports.conf` or `ss` output:

```bash
PORT=$(python3 -c "
import socket, configparser, sys

# Read already-registered ports
cfg = configparser.ConfigParser()
cfg.read('/etc/app-ports.conf')
used = {int(cfg[s]['internal']) for s in cfg.sections() if 'internal' in cfg[s]}

for p in range(8444, 8999):
    if p in used:
        continue
    try:
        s = socket.socket()
        s.bind(('127.0.0.1', p))
        s.close()
        print(p)
        break
    except OSError:
        pass
")

# Register it
cat >> /etc/app-ports.conf <<EOF

[<APPNAME>]
internal=$PORT
external=$PORT   # change to 443 if this is the primary app
EOF

echo "Allocated port: $PORT"
```

### 2c. Write Caddy snippet

```bash
FQDN=$(tailscale status --json | python3 -c \
    "import sys,json; print(json.load(sys.stdin)['Self']['DNSName'].rstrip('.'))")

# HTTPS (certs present)
cat > /etc/caddy/conf.d/<APPNAME>.caddy <<EOF
$FQDN:$PORT {
    tls /etc/ssl/tailscale/$FQDN.crt \
        /etc/ssl/tailscale/$FQDN.key
    reverse_proxy localhost:$PORT
}
EOF

# HTTP fallback (no certs — replace the block above with this instead)
# cat > /etc/caddy/conf.d/<APPNAME>.caddy <<EOF
# :80 {
#     reverse_proxy localhost:$PORT
# }
# EOF

systemctl reload caddy
```

### 2d. Write systemd service unit

Fill in `<APPNAME>`, `<SERVICE_USER>`, `<INSTALL_DIR>`, and `<START_COMMAND>`:

```ini
# /etc/systemd/system/<APPNAME>.service
[Unit]
Description=<App Display Name>
After=network.target tailscaled.service
Wants=tailscaled.service

[Service]
Type=simple
User=<SERVICE_USER>
WorkingDirectory=<INSTALL_DIR>
ExecStart=<START_COMMAND> --host 127.0.0.1 --port <PORT>
Restart=always
RestartSec=5
Environment=<APPNAME_UPPER>_SECRET_KEY=<SECRET>
Environment=<APPNAME_UPPER>_SECURE_COOKIES=<true|false>

[Install]
WantedBy=multi-user.target
```

`<APPNAME_UPPER>_SECURE_COOKIES` is `true` when TLS certs are present, `false` otherwise.  
Cookie name in the app's code must be `<APPNAME>_session` — not `session`.

```bash
systemctl daemon-reload
systemctl enable --now <APPNAME>
```

---

## Completion Checklist

```bash
# Verify service is running
systemctl status <APPNAME>

# Verify Caddy loaded the new snippet without errors
systemctl status caddy
caddy validate --config /etc/caddy/Caddyfile

# Verify port is bound
ss -tlnp | grep <PORT>

# Verify HTTPS (if certs present)
curl -sf https://<FQDN>:<PORT>/ -o /dev/null && echo OK
```

All five green → done.
