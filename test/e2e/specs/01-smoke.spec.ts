import { test } from '../helpers/fixtures'
import { signInSso, deviceUser, devicePassword } from '../helpers/auth'
import { openGeneral, sendMessage, readMessage, openAdminWorkspace, expectAdminAccess, expectNoAdminAccess } from '../helpers/rc9'
import { createUser } from '../helpers/users'
import { shoot } from '../helpers/screenshot'
import { newUserContext } from '../helpers/browser'

const memberUser = 'seconduser'
const memberPassword = 'Larkspur-Velvet-Harbor-73'
const adminUser = 'adminuser'
const adminPassword = 'Cobalt-Meadow-Lantern-58'

test('device user signs in, chats and administers (forum #655)', async ({ page }) => {
  await page.goto('/')
  await shoot(page, 'login')
  await signInSso(page, deviceUser, devicePassword)
  await shoot(page, 'logged-in')

  await openGeneral(page)
  await sendMessage(page, 'test message')
  await readMessage(page, 'test message')
  await shoot(page, 'message')

  await openAdminWorkspace(page)
  await shoot(page, 'admin-workspace')
})

test('a non-admin syncloud user signs in and has no admin access (forum #655)', async ({ browser }) => {
  await createUser(memberUser, memberPassword)

  const context = await newUserContext(browser)
  const member = await context.newPage()
  await member.goto('/')
  await signInSso(member, memberUser, memberPassword)
  await expectNoAdminAccess(member)
  await shoot(member, 'member-no-admin')
  await context.close()
})

test('a syncloud admin-group member becomes a RocketChat admin via SSO (forum #655)', async ({ browser }) => {
  await createUser(adminUser, adminPassword, true)

  const context = await newUserContext(browser)
  const admin = await context.newPage()
  await admin.goto('/')
  await signInSso(admin, adminUser, adminPassword)
  await expectAdminAccess(admin)
  await shoot(admin, 'group-admin')
  await context.close()
})
