import { promises as dns } from 'node:dns'
import * as fs from 'node:fs'
import { requireEnv } from './helpers/env'

export default async function () {
  const fullDomain = requireEnv('PLAYWRIGHT_FULL_DOMAIN')
  const appDomain = requireEnv('PLAYWRIGHT_APP_DOMAIN')
  const deviceHost = requireEnv('PLAYWRIGHT_DEVICE_HOST')

  const { address } = await dns.lookup(deviceHost)
  const entries = [
    `${address} ${fullDomain}`,
    `${address} ${appDomain}`,
    `${address} auth.${fullDomain}`,
    `${address} users.${fullDomain}`,
  ]
  fs.appendFileSync('/etc/hosts', entries.join('\n') + '\n')
}
