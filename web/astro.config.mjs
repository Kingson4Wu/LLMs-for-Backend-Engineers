import { defineConfig } from 'astro/config';
export default defineConfig({
  site: 'https://kingson4wu.github.io',
  base: process.env.SITE_BASE ?? '/Understanding-LLMs/',
  output: 'static',
  trailingSlash: 'always',
  devToolbar: { enabled: false },
});
