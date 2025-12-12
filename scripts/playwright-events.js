const { chromium } = require('playwright');

const BASE = 'https://admin.bbleads.com.br';
const CREDS = { username: 'bb@bb.com.br', password: 'bb@2024' };

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

  const apiCalls = [];
  page.on('requestfinished', async (req) => {
    const url = req.url();
    if (url.includes('api.bbleads.com.br')) {
      const res = await req.response();
      apiCalls.push({
        method: req.method(),
        url,
        status: res ? res.status() : null,
      });
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

  // Go to events page
  await page.goto(`${BASE}/event`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);

  // Try to open "Novo Evento" if present to capture additional calls
  const newButton = page.getByRole('button', { name: /novo evento|\+ ?novo/i }).first();
  if (await newButton.isVisible().catch(() => false)) {
    await Promise.all([
      newButton.click(),
      page.waitForTimeout(2000),
    ]);
  }

  await page.screenshot({ path: 'playwright-events.png', fullPage: true });
  console.log('API calls to api.bbleads.com.br:', apiCalls);

  await browser.close();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
