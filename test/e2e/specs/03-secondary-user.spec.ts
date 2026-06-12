import { test } from '../helpers/fixtures'
import { signInSso } from '../helpers/auth'
import { addUser, removeUser } from '../helpers/device'
import { shoot } from '../helpers/screenshot'

const secondaryUser = 'seconduser'
const secondaryPassword = 'Password1'

test.describe('rocketchat secondary user', () => {
  test.beforeAll(async () => {
    await addUser(secondaryUser, secondaryPassword)
  })

  test.afterAll(async () => {
    await removeUser(secondaryUser)
  })

  test('secondary syncloud user signs in via SSO (forum #655)', async ({ page }, testInfo) => {
    await page.goto('/')
    await shoot(page, testInfo, 'secondary-login')

    await signInSso(page, { user: secondaryUser, password: secondaryPassword })
    await shoot(page, testInfo, 'secondary-logged-in')
  })
})
