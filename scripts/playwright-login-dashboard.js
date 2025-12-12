const { chromium } = require('playwright');

const URL = 'https://admin.bbleads.com.br';
const CREDENTIALS = {
  username: 'bb@bb.com.br',
  password: 'bb@2024',
};

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

  await page.goto(URL, { waitUntil: 'networkidle' });
  await page.getByPlaceholder('Enter email').fill(CREDENTIALS.username);
  await page.getByPlaceholder('Enter Password').fill(CREDENTIALS.password);
  await page.getByRole('button', { name: /Acessar/i }).click();

  await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
  await page.waitForTimeout(5000);

  await page.screenshot({ path: 'playwright-dashboard.png', fullPage: true });
  console.log('API calls to api.bbleads.com.br:', apiCalls);

  await browser.close();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
