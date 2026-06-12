import { test } from '../helpers/fixtures'
import { signInSso } from '../helpers/auth'
import { installUsersApp, createUser } from '../helpers/users'
import { shoot } from '../helpers/screenshot'
import { requireEnv } from '../helpers/env'

const secondaryUser = 'seconduser'
const secondaryPassword = 'Larkspur-Velvet-Harbor-73'

test.describe('rocketchat secondary user', () => {
  test.beforeAll(async () => {
    test.setTimeout(900_000)
    await installUsersApp()
  })

  test('secondary syncloud user signs in via SSO (forum #655)', async ({ page, browser }, testInfo) => {
    test.setTimeout(300_000)
    await createUser(page, secondaryUser, secondaryPassword)
    await shoot(page, testInfo, 'user-created')

    const context = await browser.newContext({
      baseURL: `https://${requireEnv('PLAYWRIGHT_APP_DOMAIN')}`,
      ignoreHTTPSErrors: true,
      viewport: { width: 1440, height: 960 },
    })
    const rcPage = await context.newPage()

    await signInSso(rcPage, secondaryUser, secondaryPassword)
    await shoot(rcPage, testInfo, 'secondary-logged-in')
  })
})
