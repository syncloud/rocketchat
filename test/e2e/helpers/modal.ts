import { Page } from '@playwright/test'

export async function dismissStartupModal(page: Page) {
  await page.getByRole('dialog').getByRole('button', { name: 'Close' }).first()
    .click({ timeout: 15_000 }).catch(() => {})
}
