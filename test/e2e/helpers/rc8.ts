import { Page, expect } from '@playwright/test'
import { dismissStartupModal } from './modal'

export async function sendMessage(page: Page, text: string) {
  await page.goto('/channel/general')
  await dismissStartupModal(page)

  const composer = page.locator('textarea[placeholder="Message #general"]')
  await expect(composer).toBeVisible({ timeout: 30_000 })
  await composer.fill(text)
  await page.getByRole('button', { name: 'Send', exact: true }).click()

  await expect(page.getByText(text).first()).toBeVisible({ timeout: 30_000 })
}

export async function readMessage(page: Page, text: string) {
  await page.goto('/channel/general')
  await dismissStartupModal(page)
  await expect(page.getByText(text).first()).toBeVisible({ timeout: 30_000 })
}

export async function openAdminWorkspace(page: Page) {
  await page.getByRole('button', { name: 'Manage' }).click()
  await page.getByRole('menuitem', { name: 'Workspace' }).click()
  await expect(page.getByRole('heading', { name: 'Workspace' })).toBeVisible({ timeout: 30_000 })
}
