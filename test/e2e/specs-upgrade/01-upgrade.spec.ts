import { test } from '../helpers/fixtures'
import { signInSso, deviceUser, devicePassword } from '../helpers/auth'
import { sendMessage } from '../helpers/rc7'
import { readMessage, openAdminWorkspace } from '../helpers/rc8'
import { installStoreVersion, disableSetupWizard, upgradeToBuild } from '../helpers/device'
import { installUsersApp, createUser } from '../helpers/users'
import { shoot } from '../helpers/screenshot'
import { requireEnv } from '../helpers/env'

const secondaryUser = 'upgradeuser'
const secondaryPassword = 'Larkspur-Velvet-Harbor-73'

function freshContext(page: any) {
  return page.context().browser()!.newContext({
    baseURL: `https://${requireEnv('PLAYWRIGHT_APP_DOMAIN')}`,
    ignoreHTTPSErrors: true,
    viewport: { width: 1440, height: 960 },
  })
}

test.describe('rocketchat upgrade', () => {
  test('a message posted on the store version survives the upgrade and admin still works', async ({ page }, testInfo) => {
    test.setTimeout(5_400_000)

    await installStoreVersion()
    await disableSetupWizard()

    await signInSso(page, deviceUser, devicePassword)
    await shoot(page, testInfo, 'before-upgrade-home')
    await sendMessage(page, 'message before upgrade')
    await shoot(page, testInfo, 'before-upgrade-message')

    await upgradeToBuild()

    const context = await freshContext(page)
    const fresh = await context.newPage()

    await signInSso(fresh, deviceUser, devicePassword)
    await shoot(fresh, testInfo, 'after-upgrade-home')
    await readMessage(fresh, 'message before upgrade')
    await shoot(fresh, testInfo, 'after-upgrade-message')
    await openAdminWorkspace(fresh)
    await shoot(fresh, testInfo, 'after-upgrade-admin')

    await installUsersApp()
    await createUser(page, secondaryUser, secondaryPassword)
    await shoot(page, testInfo, 'after-upgrade-user-created')

    const secondaryCtx = await freshContext(page)
    const secondaryPage = await secondaryCtx.newPage()
    await signInSso(secondaryPage, secondaryUser, secondaryPassword)
    await shoot(secondaryPage, testInfo, 'after-upgrade-secondary-login')
  })
})
