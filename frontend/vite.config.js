import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import { execSync } from 'child_process'; // <-- 1. ADD THIS IMPORT

// 2. ADD THESE LINES to get build data
const commitHash = execSync('git rev-parse --short HEAD').toString().trim();
const buildDate = new Date().toISOString();
// Read version from package.json
// eslint-disable-next-line no-undef
const appVersion = process.env.npm_package_version;

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      // eslint-disable-next-line no-undef
      '@': path.resolve(__dirname, './src')
    }
  },

  // 3. ADD THIS ENTIRE 'define' BLOCK
  define: {
    // This injects the variables into your code
    'import.meta.env.VITE_APP_VERSION': JSON.stringify(appVersion),
    'import.meta.env.VITE_COMMIT_HASH': JSON.stringify(commitHash),
    'import.meta.env.VITE_BUILD_DATE': JSON.stringify(buildDate),
  },
});