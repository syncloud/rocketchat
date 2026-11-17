import { test } from '../helpers/fixtures'
import { signInSso, deviceUser, devicePassword } from '../helpers/auth'
import { openGeneral, readMessage, openAdminWorkspace, expectAdminAccess, expectNoAdminAccess } from '../helpers/rc9'
import { createUser } from '../helpers/users'
import { shoot } from '../helpers/screenshot'
import { newUserContext } from '../helpers/browser'

const memberUser = 'upgradeuser'
const memberPassword = 'Larkspur-Velvet-Harbor-73'
const adminUser = 'upgradeadmin'
const adminPassword = 'Cobalt-Meadow-Lantern-58'

test('the message survives the upgrade, admin and SSO still work', async ({ page }) => {
  await test.step('sign in after the upgrade', async () => {
    await page.goto('/')
    await signInSso(page, deviceUser, devicePassword)
    await shoot(page, 'home-after-upgrade')
  })

  await test.step('message posted before the upgrade is still there', async () => {
    await openGeneral(page)
    await readMessage(page, 'message before upgrade')
    await shoot(page, 'message-after-upgrade')
  })

  await test.step('admin workspace still opens', async () => {
    await openAdminWorkspace(page)
    await shoot(page, 'admin-after-upgrade')
  })
})

test('a non-admin syncloud user signs in after the upgrade with no admin access', async ({ browser }) => {
  await createUser(memberUser, memberPassword)

  const context = await newUserContext(browser)
  const member = await context.newPage()
  await member.goto('/')
  await signInSso(member, memberUser, memberPassword)
  await expectNoAdminAccess(member)
  await shoot(member, 'member-no-admin-after-upgrade')
  await context.close()
})

test('a syncloud admin-group member becomes a RocketChat admin via SSO after the upgrade', async ({ browser }) => {
  await createUser(adminUser, adminPassword, true)

  const context = await newUserContext(browser)
  const admin = await context.newPage()
  await admin.goto('/')
  await signInSso(admin, adminUser, adminPassword)
  await expectAdminAccess(admin)
  await shoot(admin, 'group-admin-after-upgrade')
  await context.close()
})
