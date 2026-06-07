import { test, expect } from '@playwright/test'
import { signInSso } from '../helpers/auth'
import { shoot } from '../helpers/screenshot'

test.describe('rocketchat admin rights', () => {
  test('device user signs in and has admin rights (forum #655)', async ({ page }, testInfo) => {
    await signInSso(page)
    await shoot(page, testInfo, 'logged-in')

    await page.locator('button[title="Administration"]').click()
    await page.getByText('Workspace', { exact: true }).click()
    await expect(page.getByRole('heading', { name: 'Workspace' })).toBeVisible()
    await shoot(page, testInfo, 'admin-workspace')
  })
})
