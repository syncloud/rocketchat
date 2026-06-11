import { ssh, scpFrom } from './helpers/ssh'
import * as path from 'node:path'
import * as fs from 'node:fs'
import { execSync } from 'node:child_process'
import { requireEnv } from './helpers/env'

const TMP_DIR = '/tmp/syncloud/rocketchat-ui'
const artifactRoot = requireEnv('PLAYWRIGHT_ARTIFACT_DIR')

export default async function () {
  const project = requireEnv('PLAYWRIGHT_PROJECT')
  const out = path.join(artifactRoot, 'playwright', project)
  fs.mkdirSync(out, { recursive: true })

  await ssh(`mkdir -p ${TMP_DIR}`, { throw: false })
  await ssh(`journalctl > ${TMP_DIR}/journalctl.log`, { throw: false })
  await ssh(`cp /var/snap/rocketchat/current/config/rocketchat.env ${TMP_DIR}/rocketchat.env 2>&1`, { throw: false })
  await ssh(`/snap/rocketchat/current/mongodb/bin/mongo.sh /snap/rocketchat/current/config/mongo.config.dump.js > ${TMP_DIR}/mongo.settings.dump.log 2>&1`, { throw: false })
  await scpFrom(`${TMP_DIR}/*`, out, { throw: false })
  try { execSync(`chmod -R a+r ${out}`) } catch {}
}
