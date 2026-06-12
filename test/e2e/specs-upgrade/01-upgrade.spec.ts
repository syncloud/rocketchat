import { test } from '../helpers/fixtures'
import { signInSso } from '../helpers/auth'
import { sendMessage } from '../helpers/rc7'
import { readMessage, openAdminWorkspace } from '../helpers/rc8'
import { installStoreVersion, disableSetupWizard, upgradeToBuild, addUser, removeUser } from '../helpers/device'
import { shoot } from '../helpers/screenshot'
import { requireEnv } from '../helpers/env'

const secondaryUser = 'seconduser'
const secondaryPassword = 'Password1'

function freshContext(page: any) {
  return page.context().browser()!.newContext({
    baseURL: `https://${requireEnv('PLAYWRIGHT_APP_DOMAIN')}`,
    ignoreHTTPSErrors: true,
    viewport: { width: 1440, height: 960 },
  })
}

test.describe('rocketchat upgrade', () => {
  test.afterAll(async () => {
    await removeUser(secondaryUser)
  })

  test('a message posted on the store version survives the upgrade and admin still works', async ({ page }, testInfo) => {
    test.setTimeout(5_400_000)

    await installStoreVersion()
    await disableSetupWizard()

    await signInSso(page)
    await shoot(page, testInfo, 'before-upgrade-home')
    await sendMessage(page, 'message before upgrade')
    await shoot(page, testInfo, 'before-upgrade-message')

    await upgradeToBuild()

    const context = await freshContext(page)
    const fresh = await context.newPage()

    await signInSso(fresh)
    await shoot(fresh, testInfo, 'after-upgrade-home')
    await readMessage(fresh, 'message before upgrade')
    await shoot(fresh, testInfo, 'after-upgrade-message')
    await openAdminWorkspace(fresh)
    await shoot(fresh, testInfo, 'after-upgrade-admin')

    await addUser(secondaryUser, secondaryPassword)
    const secondaryCtx = await freshContext(page)
    const secondaryPage = await secondaryCtx.newPage()
    await signInSso(secondaryPage, { user: secondaryUser, password: secondaryPassword })
    await shoot(secondaryPage, testInfo, 'after-upgrade-secondary-login')
  })
})
