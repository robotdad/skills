---
name: playwright
description: "Browser automation for validation, testing, scraping, and web interaction. Use when tasks require: (1) Navigating websites, (2) Filling forms or clicking elements, (3) Extracting data from web pages, (4) Validating UI state, (5) Capturing screenshots. Always runs headless (background) by default."
license: MIT
---

# Playwright Browser Automation

## Overview

Playwright automates Chromium, Firefox, and WebKit browsers. **Always use headless mode** — never steal focus or obscure the user's work. Capture screenshots/traces for debugging instead of watching live.

## Workflow Decision Tree

### First time using Playwright or getting dependency errors?
→ Read [`setup.md`](setup.md) for installation and environment setup

### Simple page validation or data extraction
→ Use "Basic Headless Workflow" below

### Form submission or multi-step interaction
→ Use "Basic Headless Workflow" + "Waiting Patterns" below

### Advanced tasks (auth, iframes, network mocking, mobile, parallel)
→ Read [`patterns.md`](patterns.md) for detailed patterns

### Something failing and you don't know why?
→ Read [`troubleshooting.md`](troubleshooting.md) for diagnostics

## Basic Headless Workflow

```javascript
const { chromium } = require('playwright');

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();

try {
  await page.goto('https://example.com');
  // ... actions ...
  await page.screenshot({ path: 'result.png', fullPage: true });
} finally {
  await browser.close();
}
```

## Selector Strategy (Priority Order)

```javascript
// 1. Role-based (BEST) - survives UI refactors
await page.getByRole('button', { name: 'Submit' }).click();
await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');

// 2. Label/text-based (GOOD)
await page.getByLabel('Password').fill('secret');
await page.getByText('Welcome back').isVisible();

// 3. Test ID (GOOD if available)
await page.getByTestId('submit-button').click();

// 4. CSS (sparingly) - prefer attributes over deep paths
await page.locator('[data-action="save"]').click();

// AVOID: Brittle nested selectors
// BAD: page.locator('div.container > div:nth-child(3) > ul > li a')
```

## Waiting Patterns

**Never use `waitForTimeout()`.** Use explicit waits:

```javascript
// Wait for element
await page.getByRole('button', { name: 'Submit' }).waitFor({ state: 'visible' });
await page.locator('.spinner').waitFor({ state: 'hidden' });

// Wait for navigation
await page.waitForURL('**/dashboard/**');

// Wait for network
const response = await page.waitForResponse(r => r.url().includes('/api/data'));

// Click + wait together
await Promise.all([
  page.waitForNavigation(),
  page.getByRole('link', { name: 'Next' }).click(),
]);
```

## Diagnostic Capture

```javascript
// Screenshot on failure
try {
  await doSomething();
} catch (error) {
  await page.screenshot({ path: `error-${Date.now()}.png`, fullPage: true });
  throw error;
}

// Trace for detailed debugging
await context.tracing.start({ screenshots: true, snapshots: true });
// ... actions ...
await context.tracing.stop({ path: 'trace.zip' });
// View: npx playwright show-trace trace.zip
```

## Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|-------|
| `await page.waitForTimeout(3000)` | `await locator.waitFor()` |
| `page.locator('div > div:nth-child(3) > a')` | `page.getByRole('link', { name: '...' })` |
| `headless: false` for automation | `headless: true` + screenshots |
| Swallowing errors silently | Screenshot on failure, then rethrow |
| No cleanup | `browser.close()` in finally block |

## Quick Reference

| Task | Code |
|------|------|
| Launch headless | `chromium.launch({ headless: true })` |
| Click | `page.getByRole('button', { name: 'X' }).click()` |
| Fill input | `page.getByLabel('X').fill('value')` |
| Wait visible | `locator.waitFor({ state: 'visible' })` |
| Screenshot | `page.screenshot({ path: 'x.png', fullPage: true })` |
| Get text | `locator.textContent()` |

## See Also

- [`setup.md`](setup.md) — Installation, browser binaries, system dependencies, Docker/CI
- [`patterns.md`](patterns.md) — Auth, network interception, iframes, popups, mobile, parallel execution
- [`troubleshooting.md`](troubleshooting.md) — Common errors and how to diagnose them
