import { Page } from '@playwright/test'
import { requireEnv } from './env'

export async function freshAppPage(from: Page): Promise<Page> {
  const context = await from.context().browser()!.newContext({
    baseURL: `https://${requireEnv('PLAYWRIGHT_APP_DOMAIN')}`,
    ignoreHTTPSErrors: true,
    viewport: { width: 1440, height: 960 },
  })
  return context.newPage()
}
