---
name: host-infra-discovery
description: Use when setting up a new web app on a Linux host, or when asked what's already running on monad, dyad, or any host — before writing Caddy configs, allocating ports, or creating systemd services. Determines what shared infra exists to reuse vs. what to install fresh.
---

# Host Infrastructure Discovery

## Overview

Before touching a host, inventory it. Running this prevents overwriting existing Caddy configs, allocating duplicate ports, installing duplicate cert timers, and repeating shadow group setup that's already done.

Prefix every command with `ssh <hostname>` when running against a remote host.

---

## Checklist: Run These, Then Interpret

### 1. Tailscale — FQDN and certs

```bash
tailscale status --json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['Self']['DNSName'].rstrip('.'))"
ls /etc/ssl/tailscale/ 2>/dev/null || echo "NO_CERTS"
```

| Result | Meaning |
|--------|---------|
| FQDN printed | Reuse as Caddy vhost name |
| `NO_CERTS` or empty dir | Need `tailscale cert`; HTTP fallback until then |
| `.crt` and `.key` both present | Skip cert generation |

### 2. Cert renewal timer

```bash
systemctl is-enabled tailscale-cert-renew.timer 2>/dev/null || echo "NOT_INSTALLED"
```

`enabled` → skip, don't install a second one. `NOT_INSTALLED` → install it now.

### 3. Caddy — installed, running, conf.d wired

```bash
caddy version 2>/dev/null || echo "NOT_INSTALLED"
systemctl is-active caddy 2>/dev/null || echo "NOT_RUNNING"
grep -c 'import.*conf.d' /etc/caddy/Caddyfile 2>/dev/null || echo "0"
ls /etc/caddy/conf.d/ 2>/dev/null || echo "NO_CONFD"
```

| Result | Action |
|--------|--------|
| `NOT_INSTALLED` | `apt-get install -y caddy` |
| `NOT_RUNNING` | `systemctl enable --now caddy` |
| grep returns `0` | Append `import /etc/caddy/conf.d/*.caddy` to Caddyfile |
| `NO_CONFD` | `mkdir -p /etc/caddy/conf.d` |

### 4. Port inventory — what's already allocated

```bash
cat /etc/app-ports.conf 2>/dev/null || echo "NO_REGISTRY"
ss -tlnp | awk '/127\.0\.0\.1/{print $4, $6}' | sort
```

Read the registry for intent; `ss` for reality. Any port in `ss` is taken. amplifierd is always `8410` — never reassign it.

### 5. Existing app services

```bash
systemctl list-units --type=service --state=active --no-legend \
  | grep -E 'filebrowser|amplifierd|amp-|amplifier'
```

Each running service already has a Caddy snippet — don't duplicate its vhost entry.

### 6. PAM / shadow group

```bash
getent group shadow
```

If the app's service user already appears in the output, skip `usermod`. Add once per user, not per app.

---

## Interpreting the Readout

Build this table from the six checks before writing any config:

| Component | Found | Action |
|-----------|-------|--------|
| Tailscale FQDN | `hostname.ts.net` | Use as vhost name |
| TLS certs | present / absent | Skip / `tailscale cert` |
| Cert renewal timer | enabled / not | Skip / install |
| Caddy | running + conf.d wired / partial / absent | Drop snippet / fix gaps / full install |
| Open port (8444+) | e.g. `8445` not in `ss` | Use in snippet + registry |
| Shadow group | user present / absent | Skip / `usermod -aG shadow` |

Write the new `.caddy` snippet into `conf.d/`, add the port to `/etc/app-ports.conf`, `systemctl reload caddy`. Nothing overwrites what's already there.

---

## What Never Gets Shared (Quick Reference)

| Thing | Rule |
|-------|------|
| Signing keys | Per-app at `/opt/<appname>/.secret_key` — never reused |
| Cookie names | Must be unique: `<appname>_session` — browsers don't scope by port |
| Cert renewal timer | One per host |
| Caddyfile | Never overwrite — always use `conf.d/` snippets |
| Shadow group membership | One `usermod` per user, covers all apps |
