import { ssh } from './ssh'

export async function createUser(username: string, password: string, admin = false) {
  const flag = admin ? ' --admin' : ''
  await ssh(`snap run platform.cli user add ${username} --password=${password}${flag}`)
}
