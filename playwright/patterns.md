# Playwright Advanced Patterns

## Authentication & Session Persistence

### Save and reuse auth state

```javascript
// Login and save state
const context = await browser.newContext();
const page = await context.newPage();

await page.goto('https://example.com/login');
await page.getByLabel('Email').fill('user@example.com');
await page.getByLabel('Password').fill('password');
await page.getByRole('button', { name: 'Sign In' }).click();
await page.waitForURL('**/dashboard**');

// Save cookies and localStorage
await context.storageState({ path: 'auth.json' });
await browser.close();

// Later: reuse auth state (skips login)
const authedContext = await browser.newContext({
  storageState: 'auth.json',
});
const authedPage = await authedContext.newPage();
await authedPage.goto('https://example.com/dashboard');  // Already logged in
```

### Handle login redirects

```javascript
await Promise.all([
  page.waitForURL('**/callback**'),  // OAuth redirect
  page.getByRole('button', { name: 'Login with Google' }).click(),
]);
```

## Network Interception

### Mock API responses

```javascript
await page.route('**/api/users', async route => {
  await route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify([
      { id: 1, name: 'Mocked User' },
    ]),
  });
});
```

### Modify requests

```javascript
await page.route('**/api/**', async route => {
  const headers = {
    ...route.request().headers(),
    'Authorization': 'Bearer mock-token',
  };
  await route.continue({ headers });
});
```

### Block resources (faster page loads)

```javascript
await page.route('**/*', route => {
  const blocked = ['image', 'stylesheet', 'font', 'media'];
  if (blocked.includes(route.request().resourceType())) {
    return route.abort();
  }
  return route.continue();
});
```

### Capture API responses

```javascript
const responses = [];
page.on('response', async response => {
  if (response.url().includes('/api/')) {
    responses.push({
      url: response.url(),
      status: response.status(),
      body: await response.json().catch(() => null),
    });
  }
});

await page.goto('https://example.com');
console.log('Captured API calls:', responses);
```

### Wait for specific network request

```javascript
const [response] = await Promise.all([
  page.waitForResponse(r => 
    r.url().includes('/api/search') && r.status() === 200
  ),
  page.getByRole('button', { name: 'Search' }).click(),
]);
const data = await response.json();
```

## Iframes

### Access iframe content

```javascript
// By frame name or URL
const frame = page.frame({ name: 'iframe-name' });
// or
const frame = page.frame({ url: /embed/ });

// Wait for iframe to load
const frame = await page.waitForFrame(f => f.url().includes('embed'));

// Interact with frame content
await frame.getByRole('button', { name: 'Play' }).click();
```

### FrameLocator (recommended approach)

```javascript
// Scoped locator that automatically handles frame context
const frameLocator = page.frameLocator('#my-iframe');
await frameLocator.getByRole('button', { name: 'Submit' }).click();
await frameLocator.getByLabel('Email').fill('test@example.com');

// Nested iframes
const nested = page
  .frameLocator('#outer-iframe')
  .frameLocator('#inner-iframe');
await nested.getByText('Hello').click();
```

## Popups & New Tabs

### Handle popup windows

```javascript
// Click that opens popup
const [popup] = await Promise.all([
  page.waitForEvent('popup'),
  page.getByRole('link', { name: 'Open Settings' }).click(),
]);

// Interact with popup
await popup.waitForLoadState();
await popup.getByRole('button', { name: 'Save' }).click();
await popup.close();
```

### Handle new tabs

```javascript
const [newPage] = await Promise.all([
  context.waitForEvent('page'),
  page.getByRole('link', { name: 'Open in new tab' }).click(),
]);

await newPage.waitForLoadState();
console.log('New tab URL:', newPage.url());
```

### Handle dialogs (alert, confirm, prompt)

```javascript
// Must set up listener BEFORE triggering dialog
page.on('dialog', async dialog => {
  console.log('Dialog message:', dialog.message());
  await dialog.accept();  // or dialog.dismiss()
});

await page.getByRole('button', { name: 'Delete' }).click();
```

## Mobile Emulation

### Use device presets

```javascript
const { devices } = require('playwright');
const iPhone = devices['iPhone 13'];

const context = await browser.newContext({
  ...iPhone,
});
const page = await context.newPage();
```

### Custom mobile config

```javascript
const context = await browser.newContext({
  viewport: { width: 390, height: 844 },
  deviceScaleFactor: 3,
  isMobile: true,
  hasTouch: true,
  userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)...',
});
```

### Test responsive breakpoints

```javascript
const breakpoints = [
  { name: 'mobile', width: 375, height: 667 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'desktop', width: 1440, height: 900 },
];

for (const bp of breakpoints) {
  await page.setViewportSize({ width: bp.width, height: bp.height });
  await page.screenshot({ path: `screenshot-${bp.name}.png` });
}
```

## Parallel Execution

### Multiple pages in one browser

```javascript
const browser = await chromium.launch({ headless: true });

const pages = await Promise.all([
  browser.newPage(),
  browser.newPage(),
  browser.newPage(),
]);

await Promise.all([
  pages[0].goto('https://example.com/page1'),
  pages[1].goto('https://example.com/page2'),
  pages[2].goto('https://example.com/page3'),
]);

// Process results
const titles = await Promise.all(pages.map(p => p.title()));
await browser.close();
```

### Isolated contexts (recommended for parallel)

```javascript
const browser = await chromium.launch({ headless: true });

async function scrapeUrl(url) {
  const context = await browser.newContext();  // Isolated cookies/storage
  const page = await context.newPage();
  try {
    await page.goto(url);
    return await page.title();
  } finally {
    await context.close();
  }
}

const urls = ['https://a.com', 'https://b.com', 'https://c.com'];
const results = await Promise.all(urls.map(scrapeUrl));
await browser.close();
```

### Concurrency limiting

```javascript
async function processWithLimit(items, fn, limit = 3) {
  const results = [];
  const executing = [];
  
  for (const item of items) {
    const p = fn(item).then(result => {
      executing.splice(executing.indexOf(p), 1);
      return result;
    });
    results.push(p);
    executing.push(p);
    
    if (executing.length >= limit) {
      await Promise.race(executing);
    }
  }
  
  return Promise.all(results);
}

// Usage: max 3 concurrent browsers
await processWithLimit(urls, async url => {
  const browser = await chromium.launch({ headless: true });
  // ... scrape ...
  await browser.close();
}, 3);
```

## File Operations

### Download files

```javascript
const [download] = await Promise.all([
  page.waitForEvent('download'),
  page.getByRole('button', { name: 'Export CSV' }).click(),
]);

// Save to specific path
const filePath = `./downloads/${download.suggestedFilename()}`;
await download.saveAs(filePath);
console.log('Downloaded:', filePath);

// Or get as buffer
const buffer = await download.readAsBuffer();
```

### Upload files

```javascript
// Standard file input
await page.getByLabel('Upload').setInputFiles('path/to/file.pdf');

// Multiple files
await page.getByLabel('Upload').setInputFiles([
  'file1.pdf',
  'file2.pdf',
]);

// Clear selection
await page.getByLabel('Upload').setInputFiles([]);

// Non-input uploads (dropzone, etc.)
const [fileChooser] = await Promise.all([
  page.waitForEvent('filechooser'),
  page.locator('.dropzone').click(),
]);
await fileChooser.setFiles('file.pdf');
```

## Anti-Detection

### Stealth configuration

```javascript
const browser = await chromium.launch({
  headless: true,
  args: ['--disable-blink-features=AutomationControlled'],
});

const context = await browser.newContext({
  userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  viewport: { width: 1920, height: 1080 },
  deviceScaleFactor: 2,
  locale: 'en-US',
  timezoneId: 'America/New_York',
  geolocation: { latitude: 40.7128, longitude: -74.0060 },
  permissions: ['geolocation'],
});

// Mask automation indicators
await context.addInitScript(() => {
  Object.defineProperty(navigator, 'webdriver', { get: () => false });
  Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
  Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
});
```

### Randomized delays (human-like behavior)

```javascript
function randomDelay(min = 100, max = 300) {
  return new Promise(r => setTimeout(r, min + Math.random() * (max - min)));
}

await page.getByLabel('Email').fill('user@example.com');
await randomDelay(50, 150);
await page.getByLabel('Password').fill('password');
await randomDelay(100, 200);
await page.getByRole('button', { name: 'Submit' }).click();
```

## Keyboard & Mouse

### Keyboard shortcuts

```javascript
// Single key
await page.keyboard.press('Enter');
await page.keyboard.press('Escape');

// Modifier combinations
await page.keyboard.press('Control+a');  // Select all
await page.keyboard.press('Meta+c');     // Copy (Mac)

// Type text with delay
await page.keyboard.type('Hello world', { delay: 50 });
```

### Mouse operations

```javascript
// Hover
await page.getByRole('button', { name: 'Menu' }).hover();

// Click at coordinates
await page.mouse.click(100, 200);

// Drag and drop
await page.dragAndDrop('#source', '#target');

// Or manual drag
await page.locator('#source').hover();
await page.mouse.down();
await page.locator('#target').hover();
await page.mouse.up();
```
