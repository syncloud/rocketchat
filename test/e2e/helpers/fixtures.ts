import { test as base } from '@playwright/test'
import * as path from 'node:path'
import { shoot } from './screenshot'

export { expect } from '@playwright/test'
export const test = base

base.afterEach(async ({ page }, testInfo) => {
  if (testInfo.status === testInfo.expectedStatus) {
    return
  }
  const spec = path.basename(testInfo.file, '.spec.ts')
  const stack = testInfo.errors.map((e) => e.stack ?? '').join('\n')
  const match = stack.match(new RegExp(`${spec}\\.spec\\.ts:(\\d+)`))
  const line = match ? match[1] : testInfo.line
  await shoot(page, `failed-${spec}-line-${line}`)
})
