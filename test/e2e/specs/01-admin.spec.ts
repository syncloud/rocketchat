import { test } from '../helpers/fixtures'
import { signInSso } from '../helpers/auth'
import { openAdminWorkspace } from '../helpers/rc8'
import { shoot } from '../helpers/screenshot'

test.describe('rocketchat admin rights', () => {
  test('device user signs in and has admin rights (forum #655)', async ({ page }, testInfo) => {
    await page.goto('/')
    await shoot(page, testInfo, 'login')

    await signInSso(page)
    await shoot(page, testInfo, 'logged-in')

    await openAdminWorkspace(page)
    await shoot(page, testInfo, 'admin-workspace')
  })
})
