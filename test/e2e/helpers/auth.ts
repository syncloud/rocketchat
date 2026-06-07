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

  await page.locator('#accept-button').click()

  await expect(page.locator('button[title="User menu"]')).toBeVisible({ timeout: 60_000 })
}
