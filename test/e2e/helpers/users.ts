import { Page, expect } from '@playwright/test'
import * as https from 'node:https'
import { ssh } from './ssh'
import { requireEnv } from './env'

const fullDomain = requireEnv('PLAYWRIGHT_FULL_DOMAIN')
const deviceUser = requireEnv('PLAYWRIGHT_DEVICE_USER')
const devicePassword = requireEnv('PLAYWRIGHT_DEVICE_PASSWORD')

export const usersDomain = `users.${fullDomain}`
const usersUrl = `https://${usersDomain}`

function httpStatus(url: string): Promise<number> {
  return new Promise((resolve) => {
    const req = https.get(url, { rejectUnauthorized: false }, (res: any) => {
      res.resume()
      resolve(res.statusCode ?? 0)
    })
    req.on('error', () => resolve(0))
    req.setTimeout(10_000, () => { req.destroy(); resolve(0) })
  })
}

async function waitForUsersApp(attempts = 60) {
  let ok = 0
  for (let i = 0; i < attempts; i++) {
    if (await httpStatus(`${usersUrl}/`) === 200) {
      if (++ok >= 3) return
    } else {
      ok = 0
    }
    await new Promise((r) => setTimeout(r, 10_000))
  }
  throw new Error(`users app did not answer 200 at ${usersUrl}/`)
}

export async function installUsersApp() {
  await ssh('snap install users', { throw: false, timeout: 600_000 })
  await waitForUsersApp()
}

export async function createUser(page: Page, username: string, password: string) {
  await page.goto(`${usersUrl}/`)
  await page.locator('a', { hasText: 'Log In' }).click()
  await page.locator('input[name="user_id"]').fill(deviceUser)
  await page.locator('input[name="password"]').fill(devicePassword)
  await page.locator('input[name="password"]').press('Enter')
  await expect(page.locator('a', { hasText: 'Log Out' })).toBeVisible({ timeout: 30_000 })

  await page.locator('a', { hasText: 'Account Manager' }).click()
  await page.locator('button', { hasText: 'New user' }).click()

  await page.locator('#sn').fill('Last')
  await page.locator('#givenname').fill('First')
  await page.locator('#cn').fill(username)
  await page.locator('input[name="password"]').fill(password)
  await page.locator('input[name="password_match"]').fill(password)
  await page.locator('button', { hasText: 'Create account' }).click()

  await expect(page.getByText('The account was created')).toBeVisible({ timeout: 30_000 })
}
