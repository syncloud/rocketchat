import { defineConfig, devices } from '@playwright/test'
import { requireEnv } from './helpers/env'

const fullDomain = requireEnv('PLAYWRIGHT_FULL_DOMAIN')
const appDomain = requireEnv('PLAYWRIGHT_APP_DOMAIN')
const artifactDir = requireEnv('PLAYWRIGHT_ARTIFACT_DIR')

export default defineConfig({
  testDir: requireEnv('PLAYWRIGHT_TESTDIR'),
  fullyParallel: false,
  workers: 1,
  retries: 0,
  maxFailures: 0,
  reporter: [['list']],
  outputDir: `${artifactDir}/playwright/test-results`,
  globalSetup: './globalSetup.ts',
  globalTeardown: './globalTeardown.ts',
  timeout: 120_000,
  expect: { timeout: 30_000 },
  use: {
    baseURL: `https://${appDomain}`,
    ignoreHTTPSErrors: true,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'on',
  },
  projects: [
    {
      name: 'desktop',
      use: { ...devices['Desktop Chrome'], viewport: { width: 1440, height: 960 } },
    },
  ],
  metadata: {
    appDomain,
    fullDomain,
    artifactDir,
  },
})
