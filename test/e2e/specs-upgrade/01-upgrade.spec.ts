import { test } from '../helpers/fixtures'
import { signInSso } from '../helpers/auth'
import { sendMessage } from '../helpers/rc7'
import { readMessage, openAdminWorkspace } from '../helpers/rc8'
import { installStoreVersion, disableSetupWizard, upgradeToBuild } from '../helpers/device'
import { shoot } from '../helpers/screenshot'
import { requireEnv } from '../helpers/env'

test.describe('rocketchat upgrade', () => {
  test('a message posted on the store version survives the upgrade and admin still works', async ({ page }, testInfo) => {
    test.setTimeout(5_400_000)

    await installStoreVersion()
    await disableSetupWizard()

    await signInSso(page)
    await shoot(page, testInfo, 'before-upgrade-home')
    await sendMessage(page, 'message before upgrade')
    await shoot(page, testInfo, 'before-upgrade-message')

    await upgradeToBuild()

    const context = await page.context().browser()!.newContext({
      baseURL: `https://${requireEnv('PLAYWRIGHT_APP_DOMAIN')}`,
      ignoreHTTPSErrors: true,
      viewport: { width: 1440, height: 960 },
    })
    const fresh = await context.newPage()

    await signInSso(fresh)
    await shoot(fresh, testInfo, 'after-upgrade-home')
    await readMessage(fresh, 'message before upgrade')
    await shoot(fresh, testInfo, 'after-upgrade-message')
    await openAdminWorkspace(fresh)
    await shoot(fresh, testInfo, 'after-upgrade-admin')
  })
})
