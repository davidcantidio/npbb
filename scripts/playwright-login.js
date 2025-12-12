const { chromium } = require('playwright');

const URL = 'https://admin.bbleads.com.br';
const CREDENTIALS = {
  username: 'bb@bb.com.br',
  password: 'bb@2024',
};

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });

  await page.goto(URL, { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  // Try to identify common login fields to validate against docs.
  const inputs = await page.evaluate(() =>
    Array.from(document.querySelectorAll('input')).map((el) => ({
      type: el.type,
      name: el.name || '',
      placeholder: el.placeholder || '',
      ariaLabel: el.getAttribute('aria-label') || '',
      id: el.id || '',
    })),
  );

  await page.screenshot({ path: 'playwright-login.png', fullPage: true });

  console.log('Inputs found:', inputs);
  console.log('Page title:', await page.title());

  await browser.close();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
