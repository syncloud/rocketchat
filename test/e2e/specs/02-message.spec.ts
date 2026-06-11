import { test } from '../helpers/fixtures'
import { signInSso } from '../helpers/auth'
import { sendMessage, readMessage } from '../helpers/rc8'
import { shoot } from '../helpers/screenshot'

test.describe('rocketchat messaging', () => {
  test('send and read a message in #general', async ({ page }, testInfo) => {
    await signInSso(page)
    await shoot(page, testInfo, 'logged-in')

    await sendMessage(page, 'test message')
    await shoot(page, testInfo, 'message-sent')

    await readMessage(page, 'test message')
    await shoot(page, testInfo, 'message-read')
  })
})
