import { defineConfig } from 'astro/config';
export default defineConfig({
  site: 'https://kingson4wu.github.io',
  base: process.env.SITE_BASE ?? '/LLMs-for-Backend-Engineers/',
  output: 'static',
  trailingSlash: 'always',
  devToolbar: { enabled: false },
});
