import { test, expect } from '@playwright/test'
import { signInSso } from '../helpers/auth'
import { shoot } from '../helpers/screenshot'

test.describe('rocketchat messaging', () => {
  test('send and read a message in #general', async ({ page }, testInfo) => {
    await signInSso(page)

    await page.goto('/channel/general')
    await expect(page.getByText('Start of conversation')).toBeVisible()

    const composer = page.locator('textarea[placeholder="Message #general"]')
    await composer.fill('test message')
    await composer.press('Enter')

    await expect(page.getByText('test message').first()).toBeVisible()
    await shoot(page, testInfo, 'message')
  })
})
