import * as https from 'node:https'
import * as path from 'node:path'
import { fileURLToPath } from 'node:url'
import { ssh, scpTo } from './ssh'
import { requireEnv } from './env'

const here = path.dirname(fileURLToPath(import.meta.url))
const repoRoot = path.join(here, '..', '..', '..')
const disableWizardJs = path.join(repoRoot, 'config', 'mongo.disable-wizard.js')

const appDomain = requireEnv('PLAYWRIGHT_APP_DOMAIN')

function httpStatus(url: string): Promise<number> {
  return new Promise((resolve) => {
    const req = https.get(url, { rejectUnauthorized: false }, (res: any) => {
      res.resume()
      resolve(res.statusCode ?? 0)
    })
    req.on('error', () => resolve(0))
    req.setTimeout(10_000, () => { req.destroy(); resolve(0) })
  })
}

async function waitForApp(attempts = 90) {
  let ok = 0
  for (let i = 0; i < attempts; i++) {
    if (await httpStatus(`https://${appDomain}/`) === 200) {
      if (++ok >= 3) return
    } else {
      ok = 0
    }
    await new Promise((r) => setTimeout(r, 10_000))
  }
  throw new Error(`rocketchat did not answer 200 at https://${appDomain}/`)
}

export async function installStoreVersion() {
  for (let attempt = 1; attempt <= 3; attempt++) {
    await ssh('snap remove rocketchat', { throw: false, timeout: 300_000 })
    await ssh('snap install rocketchat', { throw: false, timeout: 1_200_000 })
    try {
      await waitForApp()
      return
    } catch (e) {
      if (attempt === 3) throw e
    }
  }
}

export async function disableSetupWizard() {
  await scpTo(disableWizardJs, '/tmp/mongo.disable-wizard.js')
  await ssh('/snap/rocketchat/current/mongodb/bin/mongo.sh localhost/rocketchat /tmp/mongo.disable-wizard.js')
}

const ldapAdd = '/snap/platform/current/openldap/bin/ldapadd.sh'
const ldapDelete = '/snap/platform/current/openldap/bin/ldapdelete.sh'

export async function addUser(username: string, password: string) {
  await ssh(`snap run platform.cli user add ${username} --password=${password}`, { throw: false })
  const ldif = `dn: cn=${username},ou=groups,dc=syncloud,dc=org\\nobjectClass: posixGroup\\nobjectClass: top\\ncn: ${username}\\ngidNumber: 11\\nmemberUid: ${username}\\n`
  await ssh(`printf '${ldif}' > /tmp/${username}.group.ldif && ${ldapAdd} -x -w syncloud -D "dc=syncloud,dc=org" -f /tmp/${username}.group.ldif`)
}

export async function removeUser(username: string) {
  await ssh(`${ldapDelete} -x -w syncloud -D "dc=syncloud,dc=org" cn=${username},ou=groups,dc=syncloud,dc=org`, { throw: false })
  await ssh(`snap run platform.cli user remove ${username}`, { throw: false })
}

export async function upgradeToBuild() {
  const appArchive = requireEnv('PLAYWRIGHT_APP_ARCHIVE')
  await scpTo(appArchive, '/rocketchat.snap')
  await ssh('snap install --devmode /rocketchat.snap', { timeout: 600_000 })
  await waitForApp()
}
