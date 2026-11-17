import { defineConfig, devices } from '@playwright/test'
import { env } from './helpers/env'

const appDomain = env('PLAYWRIGHT_APP_DOMAIN')

export default defineConfig({
  testDir: './specs',
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: [['list']],
  globalSetup: './globalSetup.ts',
  globalTeardown: './globalTeardown.ts',
  timeout: 600_000,
  expect: { timeout: 30_000 },
  use: {
    baseURL: `https://${appDomain}`,
    ignoreHTTPSErrors: true,
    trace: 'off',
    screenshot: 'off',
    video: 'off',
  },
  projects: [
    {
      name: 'desktop',
      use: { ...devices['Desktop Chrome'], viewport: { width: 1440, height: 960 } },
    },
  ],
})
