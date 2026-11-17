import { test } from '../helpers/fixtures'
import { signInSso, deviceUser, devicePassword } from '../helpers/auth'
import { openGeneral, ensureMessage } from '../helpers/rc8'
import { shoot } from '../helpers/screenshot'

test('post a message on the store version', async ({ page }) => {
  await page.goto('/')
  await signInSso(page, deviceUser, devicePassword)
  await shoot(page, 'home-before-upgrade')

  await openGeneral(page)
  await ensureMessage(page, 'message before upgrade')
  await shoot(page, 'message-before-upgrade')
})
