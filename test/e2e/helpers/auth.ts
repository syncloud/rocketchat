import { Page, expect } from '@playwright/test'
import { dismissStartupModal } from './modal'
import { env } from './env'

export const deviceUser = env('PLAYWRIGHT_DEVICE_USER')
export const devicePassword = env('PLAYWRIGHT_DEVICE_PASSWORD')

export async function signInSso(page: Page, user: string, password: string) {
  await page.getByText('Login with Syncloud').click()

  await page.locator('#username-textfield').fill(user)
  await page.locator('#password-textfield').fill(password)
  await page.locator('#sign-in-button').click()

  const skipPasskey = page.getByRole('button', { name: 'Not now' })
  const userMenu = page.getByRole('button', { name: 'User menu' })
  const consent = page.locator('#accept-button')

  await expect(skipPasskey.or(userMenu).or(consent)).toBeVisible({ timeout: 60_000 })
  if (await skipPasskey.isVisible()) {
    await skipPasskey.click()
  }

  await expect(userMenu.or(consent)).toBeVisible({ timeout: 60_000 })
  if (await consent.isVisible()) {
    await consent.click()
  }

  await expect(userMenu).toBeVisible({ timeout: 60_000 })

  await dismissStartupModal(page)
}
