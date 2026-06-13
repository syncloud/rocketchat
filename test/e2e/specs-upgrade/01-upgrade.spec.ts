import { test } from '../helpers/fixtures'
import { signInSso, deviceUser, devicePassword } from '../helpers/auth'
import { sendMessage } from '../helpers/rc7'
import { readMessage, openAdminWorkspace } from '../helpers/rc8'
import { installStoreVersion, disableSetupWizard, upgradeToBuild } from '../helpers/device'
import { installUsersApp, createUser } from '../helpers/users'
import { freshAppPage } from '../helpers/context'
import { shoot } from '../helpers/screenshot'

const secondaryUser = 'upgradeuser'
const secondaryPassword = 'Larkspur-Velvet-Harbor-73'

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

    const fresh = await freshAppPage(page)
    await signInSso(fresh, deviceUser, devicePassword)
    await shoot(fresh, testInfo, 'after-upgrade-home')
    await readMessage(fresh, 'message before upgrade')
    await shoot(fresh, testInfo, 'after-upgrade-message')
    await openAdminWorkspace(fresh)
    await shoot(fresh, testInfo, 'after-upgrade-admin')

    await installUsersApp()
    await createUser(page, secondaryUser, secondaryPassword)
    await shoot(page, testInfo, 'after-upgrade-user-created')

    const secondaryPage = await freshAppPage(page)
    await signInSso(secondaryPage, secondaryUser, secondaryPassword)
    await shoot(secondaryPage, testInfo, 'after-upgrade-secondary-login')
  })
})
