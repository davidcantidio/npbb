const { chromium } = require('playwright');

const BASE = 'https://admin.bbleads.com.br';
const CREDS = { username: 'bb@bb.com.br', password: 'bb@2024' };
const EVENT_ID = '194';

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  page.setDefaultNavigationTimeout(45000);

  const apiCalls = [];
  page.on('requestfinished', async (req) => {
    const url = req.url();
    if (url.includes('api.bbleads.com.br')) {
      const res = await req.response();
      apiCalls.push({ method: req.method(), url, status: res ? res.status() : null });
    }
  });

  // Login
  await page.goto(BASE, { waitUntil: 'networkidle' });
  await page.waitForSelector('input[placeholder="Enter email"]', { timeout: 10000 });
  await page.getByPlaceholder('Enter email').fill(CREDS.username);
  await page.getByPlaceholder('Enter Password').fill(CREDS.password);
  await Promise.all([
    page.waitForResponse((res) => res.url().includes('/auth/login'), { timeout: 15000 }),
    page.getByRole('button', { name: /Acessar/i }).click(),
  ]);
  await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
  await page.waitForTimeout(2000);

  // Go to events list
  await page.goto(`${BASE}/event`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: 'playwright-event194-list.png', fullPage: true });

  const row = page.locator('tr', { hasText: EVENT_ID }).first();
  await row.scrollIntoViewIfNeeded();

  const actionLinks = row.locator('a');

  // View icon (assume first link)
  if (await actionLinks.count().then((c) => c > 0)) {
    await actionLinks.nth(0).click();
    await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'playwright-event194-view.png', fullPage: true });
    await page.goBack();
    await page.waitForTimeout(2000);
  }

  // Edit icon (assume second link)
  if (await actionLinks.count().then((c) => c > 1)) {
    await actionLinks.nth(1).click();
    await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'playwright-event194-edit.png', fullPage: true });
    await page.goBack();
    await page.waitForTimeout(2000);
  }

  // Delete icon (assume third link) — cancel immediately
  if (await actionLinks.count().then((c) => c > 2)) {
    await actionLinks.nth(2).click();
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'playwright-event194-delete-modal.png', fullPage: true });
    const cancelBtn = page.getByRole('button', { name: /não|nao|cancelar/i }).first();
    if (await cancelBtn.isVisible().catch(() => false)) {
      await cancelBtn.click();
    } else {
      await page.keyboard.press('Escape');
    }
    await page.waitForTimeout(1000);
  }

  console.log('API calls:', apiCalls);
  await browser.close();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
