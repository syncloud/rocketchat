import { Page, TestInfo } from '@playwright/test'
import * as path from 'node:path'
import * as fs from 'node:fs'
import { requireEnv } from './env'

const artifactRoot = requireEnv('PLAYWRIGHT_ARTIFACT_DIR')

export async function shoot(page: Page, testInfo: TestInfo, name: string) {
  const view = testInfo.project.name
  const dir = path.join(artifactRoot, 'playwright', view, 'screenshot')
  fs.mkdirSync(dir, { recursive: true })
  await page.screenshot({ path: path.join(dir, `${name}-${view}.png`), fullPage: false })
  fs.writeFileSync(path.join(dir, `${name}-${view}.html`), await page.content())
}
