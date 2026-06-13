import { Page, expect } from '@playwright/test'
import { dismissStartupModal } from './modal'
import { requireEnv } from './env'

export const deviceUser = requireEnv('PLAYWRIGHT_DEVICE_USER')
export const devicePassword = requireEnv('PLAYWRIGHT_DEVICE_PASSWORD')

export async function signInSso(page: Page, user: string, password: string) {
  await page.goto('/')
  await page.getByText('Login with Syncloud').click()

  await page.locator('#username-textfield').fill(user)
  await page.locator('#password-textfield').fill(password)
  await page.locator('#sign-in-button').click()

  const userMenu = page.getByRole('button', { name: 'User menu' })
  const consent = page.locator('#accept-button')
  await expect(userMenu.or(consent)).toBeVisible({ timeout: 60_000 })
  if (await consent.isVisible()) {
    await consent.click()
  }

  await expect(userMenu).toBeVisible({ timeout: 60_000 })

  await dismissStartupModal(page)
}
