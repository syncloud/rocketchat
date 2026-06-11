import { test as base } from '@playwright/test'
import { shoot } from './screenshot'

export { expect } from '@playwright/test'
export const test = base

base.afterEach(async ({ page }, testInfo) => {
  if (testInfo.status !== testInfo.expectedStatus) {
    const name = 'failed-' + testInfo.title.replace(/[^a-z0-9]+/gi, '-').toLowerCase()
    await shoot(page, testInfo, name)
  }
})
