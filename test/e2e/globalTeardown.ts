import * as fs from 'node:fs'
import { execSync } from 'node:child_process'
import { ssh, scpFrom } from './helpers/ssh'
import { env } from './helpers/env'

const TMP_DIR = '/tmp/syncloud/rocketchat-ui'

export default async function () {
  const out = env('PLAYWRIGHT_LOG_DIR')
  fs.mkdirSync(out, { recursive: true })

  await ssh(`mkdir -p ${TMP_DIR}`, { throw: false })
  await ssh(`journalctl > ${TMP_DIR}/journalctl.log`, { throw: false })
  await ssh(`cp /var/snap/rocketchat/current/config/rocketchat.env ${TMP_DIR}/rocketchat.env`, { throw: false })
  await ssh(`/snap/rocketchat/current/mongodb/bin/mongo.sh /snap/rocketchat/current/config/mongo.config.dump.js > ${TMP_DIR}/mongo.settings.dump.log 2>&1`, { throw: false })
  await scpFrom(`${TMP_DIR}/*`, out, { throw: false })
  execSync(`chmod -R a+r ${out}`)
}
