import { defineConfig } from 'vitest/config'

export default defineConfig({ test: { root: import.meta.dirname, include: ['site/themes/**/*.test.ts'] } })
