import { promises as dns } from 'node:dns'
import * as fs from 'node:fs'
import { env } from './helpers/env'

export default async function () {
  const fullDomain = env('PLAYWRIGHT_FULL_DOMAIN')
  const appDomain = env('PLAYWRIGHT_APP_DOMAIN')
  const deviceHost = env('PLAYWRIGHT_DEVICE_HOST')

  const { address } = await dns.lookup(deviceHost)
  const entries = [
    `${address} ${fullDomain}`,
    `${address} ${appDomain}`,
    `${address} auth.${fullDomain}`,
  ]
  fs.appendFileSync('/etc/hosts', entries.join('\n') + '\n')
}
