import { Page, expect } from '@playwright/test'

const deviceUser = required('PLAYWRIGHT_DEVICE_USER')
const devicePassword = required('PLAYWRIGHT_DEVICE_PASSWORD')

function required(name: string): string {
  const v = process.env[name]
  if (!v) throw new Error(`${name} is required`)
  return v
}

export async function signInSso(page: Page) {
  await page.goto('/')
  await page.getByText('Login with Syncloud').click()

  await page.locator('#username-textfield').fill(deviceUser)
  await page.locator('#password-textfield').fill(devicePassword)
  await page.locator('#sign-in-button').click()

  const userMenu = page.locator('button[title="User menu"]')
  const consent = page.locator('#accept-button')
  await expect(userMenu.or(consent)).toBeVisible({ timeout: 60_000 })
  if (await consent.isVisible()) {
    await consent.click()
  }

  await expect(userMenu).toBeVisible({ timeout: 60_000 })
}
