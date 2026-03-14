const { chromium } = require('playwright');

const BASE = 'https://admin.bbleads.com.br';
const CREDS = { username: 'bb@bb.com.br', password: 'bb@2024' };
const EVENT_ID = 185;

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  page.setDefaultNavigationTimeout(45000);

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

  // Open event detail
  await page.goto(`${BASE}/event/${EVENT_ID}/general`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);

  // Screenshot aba Evento
  await page.screenshot({ path: 'playwright-event-detail-evento.png', fullPage: true });

  // Helper to click tab by text and screenshot
  async function clickTabAndShot(labelRegex, file) {
    const tab = page.getByText(labelRegex, { exact: false });
    if (await tab.isVisible().catch(() => false)) {
      await tab.click();
      await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {});
      await page.waitForTimeout(2000);
      await page.screenshot({ path: file, fullPage: true });
    }
  }

  await clickTabAndShot(/Landing Page/i, 'playwright-event-detail-lead.png');
  await clickTabAndShot(/Gamifica/i, 'playwright-event-detail-gamificacao.png');
  await clickTabAndShot(/Ativaç/i, 'playwright-event-detail-ativacoes.png');
  await clickTabAndShot(/Questionário/i, 'playwright-event-detail-questionario.png');

  console.log('API calls to api.bbleads.com.br:', apiCalls);

  await browser.close();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
