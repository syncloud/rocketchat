import { Browser, BrowserContext } from '@playwright/test'
import { env } from './env'

export async function newUserContext(browser: Browser): Promise<BrowserContext> {
  return browser.newContext({
    baseURL: `https://${env('PLAYWRIGHT_APP_DOMAIN')}`,
    ignoreHTTPSErrors: true,
    viewport: { width: 1440, height: 960 },
  })
}
