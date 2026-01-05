# Playwright Setup Guide

## Quick Install

```bash
# Install Playwright
npm install playwright

# Install browser binaries (REQUIRED)
npx playwright install

# Or install specific browser only
npx playwright install chromium
```

## System Dependencies (Linux)

Headless Chromium requires system libraries. If you get errors about missing `.so` files:

```bash
# Install all dependencies automatically
npx playwright install-deps

# Or for Chromium only
npx playwright install-deps chromium
```

### Manual dependency install (Debian/Ubuntu)

```bash
sudo apt-get update
sudo apt-get install -y \
  libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
  libcups2 libdrm2 libdbus-1-3 libxkbcommon0 \
  libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
  libgbm1 libasound2 libpango-1.0-0 libcairo2
```

## Docker Setup

### Recommended: Use Playwright's official image

```dockerfile
FROM mcr.microsoft.com/playwright:v1.40.0-jammy

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
```

### Custom Dockerfile

```dockerfile
FROM node:20-slim

RUN npx playwright install --with-deps chromium

WORKDIR /app
COPY . .
RUN npm install
```

### Docker run flags for headless

```bash
# Usually works without special flags in headless mode
docker run my-playwright-app

# If you have issues, try:
docker run --ipc=host my-playwright-app

# For headed mode (debugging only), you need X11:
docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix my-playwright-app
```

## CI/CD Setup

### GitHub Actions

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npx playwright test
```

### GitLab CI

```yaml
test:
  image: mcr.microsoft.com/playwright:v1.40.0-jammy
  script:
    - npm ci
    - npx playwright test
```

## Browser Binary Locations

Playwright downloads browsers to a cache directory:

```bash
# Default locations
# Linux: ~/.cache/ms-playwright
# macOS: ~/Library/Caches/ms-playwright
# Windows: %USERPROFILE%\AppData\Local\ms-playwright

# Check current browser installations
npx playwright --version

# Force re-download
npx playwright install --force
```

### Custom browser path

```bash
# Set custom cache directory
export PLAYWRIGHT_BROWSERS_PATH=/custom/path
npx playwright install
```

```javascript
// Or in code, use executable path directly
const browser = await chromium.launch({
  executablePath: '/path/to/chrome',
});
```

## Using System Chrome Instead of Bundled

```javascript
const browser = await chromium.launch({
  channel: 'chrome',  // Uses installed Chrome
  // or: channel: 'chrome-beta', 'chrome-dev', 'msedge'
});
```

## Verify Installation

```bash
# Quick verification script
npx playwright install chromium
node -e "
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto('https://example.com');
  console.log('Title:', await page.title());
  await browser.close();
  console.log('✓ Playwright working correctly');
})();
"
```

## Common Setup Errors

| Error | Solution |
|-------|----------|
| `browserType.launch: Executable doesn't exist` | Run `npx playwright install` |
| `error while loading shared libraries: libnss3.so` | Run `npx playwright install-deps` |
| `Failed to launch browser: spawn EACCES` | Check file permissions on browser binary |
| `Protocol error: Connection closed` | In Docker, try `--ipc=host` flag |
| `Target closed` on launch | Increase launch timeout or check system resources |

## Resource Configuration

```javascript
const browser = await chromium.launch({
  headless: true,
  args: [
    '--disable-gpu',              // Reduce resource usage
    '--disable-dev-shm-usage',    // Fix for Docker
    '--no-sandbox',               // Required in some CI environments (use with caution)
    '--disable-setuid-sandbox',
  ],
});

// Limit context resources
const context = await browser.newContext({
  viewport: { width: 1280, height: 720 },
  deviceScaleFactor: 1,  // Lower = less memory
});
```
