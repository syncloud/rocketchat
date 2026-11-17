import { Page, expect } from '@playwright/test'
import { dismissStartupModal } from './modal'

const composerPlaceholder = 'Message #general'

export async function openGeneral(page: Page) {
  await page.locator('a[href="/channel/general"]').first().click()
  await dismissStartupModal(page)
  await expect(page.locator(`textarea[placeholder="${composerPlaceholder}"]`)).toBeVisible()
}

export async function sendMessage(page: Page, text: string) {
  const composer = page.locator(`textarea[placeholder="${composerPlaceholder}"]`)
  await composer.fill(text)
  await page.getByRole('button', { name: 'Send', exact: true }).click()
  await expect(page.getByText(text).first()).toBeVisible()
}

export async function ensureMessage(page: Page, text: string) {
  const message = page.getByText(text).first()
  if (await message.isVisible({ timeout: 10_000 }).catch(() => false)) {
    return
  }
  await sendMessage(page, text)
}

export async function readMessage(page: Page, text: string) {
  await expect(page.getByText(text).first()).toBeVisible()
}

export async function openAdminWorkspace(page: Page) {
  await page.getByRole('button', { name: 'Manage' }).click()
  await page.getByRole('menuitem', { name: 'Workspace' }).click()
  await expect(page.getByRole('heading', { name: 'Workspace' })).toBeVisible()
}
