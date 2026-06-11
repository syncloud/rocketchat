import { Page, expect } from '@playwright/test'
import { dismissStartupModal } from './modal'

export async function sendMessage(page: Page, text: string) {
  await page.goto('/channel/general')
  await dismissStartupModal(page)

  const composer = page.locator('textarea[placeholder="Message #general"]')
  await expect(composer).toBeVisible({ timeout: 30_000 })
  await composer.fill(text)
  await composer.press('Enter')

  await expect(page.getByText(text).first()).toBeVisible({ timeout: 30_000 })
}
