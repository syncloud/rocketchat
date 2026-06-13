import { test } from '../helpers/fixtures'
import { signInSso } from '../helpers/auth'
import { installUsersApp, createUser } from '../helpers/users'
import { freshAppPage } from '../helpers/context'
import { shoot } from '../helpers/screenshot'

const secondaryUser = 'seconduser'
const secondaryPassword = 'Larkspur-Velvet-Harbor-73'

test.describe('rocketchat secondary user', () => {
  test.beforeAll(async () => {
    test.setTimeout(900_000)
    await installUsersApp()
  })

  test('secondary syncloud user signs in via SSO (forum #655)', async ({ page }, testInfo) => {
    test.setTimeout(300_000)
    await createUser(page, secondaryUser, secondaryPassword)
    await shoot(page, testInfo, 'user-created')

    const rcPage = await freshAppPage(page)
    await signInSso(rcPage, secondaryUser, secondaryPassword)
    await shoot(rcPage, testInfo, 'secondary-logged-in')
  })
})
