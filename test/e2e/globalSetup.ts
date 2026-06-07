import { promises as dns } from 'node:dns'
import * as fs from 'node:fs'

export default async function () {
  const fullDomain = process.env.PLAYWRIGHT_FULL_DOMAIN ?? 'buster.com'
  const appDomain = process.env.PLAYWRIGHT_APP_DOMAIN ?? `rocketchat.${fullDomain}`
  const deviceHost = process.env.PLAYWRIGHT_DEVICE_HOST ?? fullDomain

  const { address } = await dns.lookup(deviceHost)
  const entries = [
    `${address} ${fullDomain}`,
    `${address} ${appDomain}`,
    `${address} auth.${fullDomain}`,
  ]
  fs.appendFileSync('/etc/hosts', entries.join('\n') + '\n')
}
