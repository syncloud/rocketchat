import { execFile } from 'node:child_process'
import { requireEnv } from './env'

export const deviceHost = requireEnv('PLAYWRIGHT_DEVICE_HOST')
export const sshUser = requireEnv('PLAYWRIGHT_SSH_USER')
export const sshPassword = requireEnv('PLAYWRIGHT_SSH_PASSWORD')

const baseArgs = [
  '-o', 'StrictHostKeyChecking=no',
  '-o', 'UserKnownHostsFile=/dev/null',
  '-o', 'LogLevel=ERROR',
]

function run(args: string[], timeout: number): Promise<string> {
  return new Promise((resolve, reject) => {
    execFile('sshpass', args, { encoding: 'utf8', timeout, maxBuffer: 16 * 1024 * 1024 }, (err: any, stdout, stderr) => {
      if (err) {
        err.stdout = stdout
        err.stderr = stderr
        err.message = `${err.message}\n${stderr ?? ''}${stdout ?? ''}`.trim()
        reject(err)
      } else {
        resolve(stdout)
      }
    })
  })
}

export async function ssh(cmd: string, opts: { throw?: boolean, timeout?: number } = {}): Promise<string> {
  const args = ['-p', sshPassword, 'ssh', ...baseArgs, `${sshUser}@${deviceHost}`, cmd]
  try {
    return await run(args, opts.timeout ?? 120_000)
  } catch (e: any) {
    if (opts.throw === false) {
      return (e.stdout?.toString() ?? '') + (e.stderr?.toString() ?? '')
    }
    throw e
  }
}

export async function scpFrom(remote: string, local: string, opts: { throw?: boolean } = {}): Promise<void> {
  const args = ['-p', sshPassword, 'scp', ...baseArgs, '-r', `${sshUser}@${deviceHost}:${remote}`, local]
  try {
    await run(args, 120_000)
  } catch (e) {
    if (opts.throw !== false) throw e
  }
}

export async function scpTo(local: string, remote: string): Promise<void> {
  const args = ['-p', sshPassword, 'scp', ...baseArgs, local, `${sshUser}@${deviceHost}:${remote}`]
  await run(args, 120_000)
}
