import { chromium, type Browser, type BrowserContext, type Page, type ViewportSize } from "playwright";

export interface BrowserLaunchOptions {
  headless: boolean;
}

export interface BrowserContextOptions {
  storageStatePath?: string | null;
  viewport?: ViewportSize;
  userAgent?: string;
  locale?: string;
}

export interface PageDefaults {
  timeoutMs?: number;
  navigationTimeoutMs?: number;
}

export async function launchBrowser(options: BrowserLaunchOptions): Promise<Browser> {
  return chromium.launch({ headless: options.headless });
}

export async function newContext(browser: Browser, options: BrowserContextOptions): Promise<BrowserContext> {
  return browser.newContext({
    storageState: options.storageStatePath ?? undefined,
    viewport: options.viewport ?? { width: 1280, height: 720 },
    userAgent: options.userAgent,
    locale: options.locale,
  });
}

export async function newPageWithDefaults(context: BrowserContext, defaults: PageDefaults = {}): Promise<Page> {
  const page = await context.newPage();
  const timeoutMs = defaults.timeoutMs ?? 30_000;
  page.setDefaultTimeout(timeoutMs);
  page.setDefaultNavigationTimeout(defaults.navigationTimeoutMs ?? timeoutMs);
  return page;
}

