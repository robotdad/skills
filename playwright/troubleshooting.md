# Playwright Troubleshooting

## Diagnostic First Steps

When something fails, capture diagnostics before changing anything:

```javascript
try {
  await doSomething();
} catch (error) {
  // Capture current state
  await page.screenshot({ path: 'error-screenshot.png', fullPage: true });
  console.log('Current URL:', page.url());
  console.log('Page title:', await page.title());
  console.log('Error:', error.message);
  throw error;
}
```

### Enable tracing for detailed debugging

```javascript
const context = await browser.newContext();
await context.tracing.start({ 
  screenshots: true, 
  snapshots: true,
  sources: true,
});

const page = await context.newPage();
// ... your code ...

// Save trace on failure
await context.tracing.stop({ path: 'trace.zip' });

// View trace:
// npx playwright show-trace trace.zip
```

## Common Errors & Solutions

### "Executable doesn't exist at path"

**Cause:** Browser binaries not installed.

```bash
# Fix
npx playwright install

# Or specific browser
npx playwright install chromium
```

### "error while loading shared libraries: lib*.so"

**Cause:** Missing system dependencies (Linux).

```bash
# Fix: Install all dependencies
npx playwright install-deps

# Or manual (Debian/Ubuntu)
sudo apt-get install libnss3 libatk1.0-0 libatk-bridge2.0-0 \
  libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 \
  libxfixes3 libxrandr2 libgbm1 libasound2
```

### "Timeout 30000ms exceeded"

**Causes:**
1. Element doesn't exist
2. Element exists but not visible/enabled
3. Wrong selector
4. Page still loading
5. Network is slow

**Debug steps:**

```javascript
// 1. Check if element exists at all
const count = await page.locator('your-selector').count();
console.log('Elements found:', count);

// 2. Check element state
const locator = page.locator('your-selector');
console.log('Visible:', await locator.isVisible().catch(() => 'error'));
console.log('Enabled:', await locator.isEnabled().catch(() => 'error'));

// 3. Screenshot current state
await page.screenshot({ path: 'debug.png', fullPage: true });

// 4. Increase timeout for slow pages
await locator.click({ timeout: 60000 });

// 5. Wait for network to settle first
await page.waitForLoadState('networkidle');
```

### "Element is not visible"

**Causes:**
1. Element hidden by CSS
2. Element off-screen
3. Element covered by another element
4. Element inside closed accordion/dropdown

```javascript
// Force action (use sparingly)
await page.locator('selector').click({ force: true });

// Scroll element into view first
await page.locator('selector').scrollIntoViewIfNeeded();
await page.locator('selector').click();

// Wait for element to become visible
await page.locator('selector').waitFor({ state: 'visible' });
```

### "Element is outside of the viewport"

```javascript
// Scroll into view
await page.locator('selector').scrollIntoViewIfNeeded();

// Or use larger viewport
const context = await browser.newContext({
  viewport: { width: 1920, height: 1080 },
});
```

### "Strict mode violation: locator resolved to N elements"

**Cause:** Selector matches multiple elements.

```javascript
// Find which elements match
const count = await page.locator('button').count();
console.log('Found', count, 'buttons');

// Solutions:

// 1. Be more specific
await page.getByRole('button', { name: 'Submit' }).click();

// 2. Use first/nth
await page.locator('button').first().click();
await page.locator('button').nth(2).click();

// 3. Filter by text or other attribute
await page.locator('button').filter({ hasText: 'Submit' }).click();
```

### "Target page, context or browser has been closed"

**Cause:** Browser/page closed unexpectedly or race condition.

```javascript
// Check if page is still open before acting
if (!page.isClosed()) {
  await page.click('selector');
}

// Handle navigation that closes page
const [newPage] = await Promise.all([
  context.waitForEvent('page'),
  page.click('link-that-opens-new-page'),
]);
// Original page may be closed, use newPage
```

### "net::ERR_NAME_NOT_RESOLVED" or network errors

**Causes:**
1. Invalid URL
2. Network connectivity issue
3. DNS failure

```javascript
// Check URL is valid
console.log('Navigating to:', url);

// Handle network errors gracefully
try {
  await page.goto(url, { timeout: 30000 });
} catch (error) {
  if (error.message.includes('net::')) {
    console.log('Network error - site may be down');
  }
  throw error;
}
```

### Navigation timeout

```javascript
// Increase navigation timeout
await page.goto(url, { 
  timeout: 60000,
  waitUntil: 'domcontentloaded',  // Don't wait for all resources
});

// Or wait for specific element instead of full load
await page.goto(url, { waitUntil: 'commit' });
await page.locator('#main-content').waitFor();
```

## Selector Debugging

### Find out why selector doesn't match

```javascript
// Check what's actually on the page
const html = await page.content();
console.log(html);

// Or evaluate in browser context
await page.evaluate(() => {
  console.log(document.querySelector('your-selector'));
  console.log(document.querySelectorAll('your-selector').length);
});

// Test selector in browser devtools first:
// $$('your-selector') in console
```

### Debug role-based selectors

```javascript
// Get accessibility tree
const snapshot = await page.accessibility.snapshot();
console.log(JSON.stringify(snapshot, null, 2));

// Check element's accessible name
const name = await page.locator('button').first().getAttribute('aria-label');
console.log('Button accessible name:', name);
```

## Timing Issues

### Race condition between click and navigation

```javascript
// WRONG - may miss the navigation
await page.click('a');
await page.waitForURL('**/next-page');

// RIGHT - wait for both together
await Promise.all([
  page.waitForURL('**/next-page'),
  page.click('a'),
]);
```

### Element appears then disappears (loading states)

```javascript
// Wait for loading indicator to appear AND disappear
await page.locator('.loading').waitFor({ state: 'visible' });
await page.locator('.loading').waitFor({ state: 'hidden' });

// Or wait for final content
await page.locator('.results').waitFor({ state: 'visible' });
```

### Action happens before element is ready

```javascript
// Wait for element to be actionable
await page.locator('button').waitFor({ state: 'visible' });

// Check if enabled
await page.locator('button').isEnabled();

// Playwright auto-waits, but for dynamic JS apps:
await page.waitForFunction(() => {
  const btn = document.querySelector('button');
  return btn && !btn.disabled && btn.offsetParent !== null;
});
```

## Docker & CI Issues

### "Protocol error: Connection closed"

```bash
# Try IPC namespace sharing
docker run --ipc=host your-image
```

### Browser crashes in Docker

```javascript
const browser = await chromium.launch({
  headless: true,
  args: [
    '--disable-dev-shm-usage',  // Use /tmp instead of /dev/shm
    '--no-sandbox',             // Required in some containers
    '--disable-setuid-sandbox',
    '--disable-gpu',
  ],
});
```

### Out of memory

```javascript
// Close contexts/pages when done
await page.close();
await context.close();

// Don't accumulate browsers
const browser = await chromium.launch();
try {
  // ... work ...
} finally {
  await browser.close();
}

// Reduce memory with smaller viewport
const context = await browser.newContext({
  viewport: { width: 800, height: 600 },
  deviceScaleFactor: 1,
});
```

## Headed Mode Debugging (Last Resort)

When all else fails, watch what's happening:

```javascript
const browser = await chromium.launch({
  headless: false,
  slowMo: 500,  // Slow down actions to observe
});

// Or pause execution
await page.pause();  // Opens inspector
```

## Getting More Information

### Enable Playwright debug logging

```bash
# See all Playwright logs
DEBUG=pw:api node your-script.js

# Browser-specific logs
DEBUG=pw:browser node your-script.js
```

### Log all network traffic

```javascript
page.on('request', r => console.log('>>', r.method(), r.url()));
page.on('response', r => console.log('<<', r.status(), r.url()));
page.on('requestfailed', r => console.log('FAILED:', r.url(), r.failure()?.errorText));
```

### Log console messages from page

```javascript
page.on('console', msg => {
  console.log(`Browser [${msg.type()}]: ${msg.text()}`);
});

page.on('pageerror', err => {
  console.log('Page error:', err.message);
});
```
