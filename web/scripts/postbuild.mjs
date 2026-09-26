import fs from 'node:fs';
import path from 'node:path';
import { catalog, pages, locales, bookDir } from '../src/lib/book.mjs';
import { chapterUrl, withBase } from '../src/lib/paths.mjs';
const base = process.env.SITE_BASE ?? '/LLMs-for-Backend-Engineers/';
const dist = new URL('../dist/', import.meta.url);
const write = (file, text) => {
  const target = new URL(file, dist);
  fs.mkdirSync(path.dirname(target.pathname), { recursive: true });
  fs.writeFileSync(target, text);
};
const escape = (s) =>
  s.replaceAll('&', '&amp;').replaceAll('"', '&quot;').replaceAll('<', '&lt;');
for (const page of pages) {
  const file =
    page.path === 'index.md'
      ? 'introduction.html'
      : page.path.replace(/\.md$/, '.html');
  const href = chapterUrl('zh-Hans', page.id, base);
  write(
    file,
    `<!doctype html><html lang="zh-Hans"><head><meta charset="utf-8"><meta name="robots" content="noindex"><link rel="canonical" href="https://kingson4wu.github.io${href}"><title>${escape(page.title)}</title></head><body><a href="${href}">本页已迁移，继续阅读 / Continue reading</a><script>location.replace(${JSON.stringify(href)}+location.hash)</script></body></html>`,
  );
}
const retiredChapterRedirects = [
  { id: 'ai-math-essentials', target: 'math-foundations' },
  {
    id: 'attention-mechanism',
    target: 'transformer-architecture',
    legacyFile: 'chapters/part2-llm-internal/attention-mechanism.html',
  },
];
for (const locale of locales) {
  for (const redirect of retiredChapterRedirects) {
    const href = chapterUrl(locale, redirect.target, base);
    const redirectPage = '<!doctype html><html lang="' + locale + '"><head><meta charset="utf-8"><meta name="robots" content="noindex"><link rel="canonical" href="https://kingson4wu.github.io' + href + '"><title>Moved page</title></head><body><a href="' + href + '">本页已并入 Transformer 架构，继续阅读 / This page now belongs to the Transformer chapter</a><script>location.replace(' + JSON.stringify(href) + '+location.hash)</script></body></html>';
    write(locale + '/read/' + redirect.id + '/index.html', redirectPage);
    if (locale === 'zh-Hans' && redirect.legacyFile)
      write(redirect.legacyFile, redirectPage);
  }
}
fs.cpSync(path.join(bookDir, 'assets'), new URL('assets/', dist), {
  recursive: true,
});
const exported = path.join(bookDir, 'exported');
if (fs.existsSync(exported)) {
  for (const locale of locales) {
    const dir = path.join(exported, locale);
    if (fs.existsSync(dir)) {
      fs.mkdirSync(new URL(`exported/${locale}/`, dist), { recursive: true });
      for (const file of [
        'book.pdf',
        'book.epub',
        'book-print.html',
        'manifest.json',
      ])
        if (fs.existsSync(path.join(dir, file)))
          fs.copyFileSync(
            path.join(dir, file),
            new URL(`exported/${locale}/${file}`, dist),
          );
    }
  }
}
// Keep the historic PDF URL available once a real PDF is present.
if (fs.existsSync(path.join(exported, 'zh-Hans/book.pdf'))) {
  fs.mkdirSync(new URL('exported/', dist), { recursive: true });
  fs.copyFileSync(
    path.join(exported, 'zh-Hans/book.pdf'),
    new URL('exported/book.pdf', dist),
  );
}
const urls = locales.flatMap((l) => [
  withBase(`/${l}/`, base),
  withBase(`/${l}/downloads/`, base),
  ...pages.map((p) => chapterUrl(l, p.id, base)),
]);
write(
  'sitemap.xml',
  `<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${urls.map((u) => `<url><loc>https://kingson4wu.github.io${u}</loc></url>`).join('')}</urlset>`,
);
write(
  'robots.txt',
  process.env.SITE_PREVIEW === 'true'
    ? 'User-agent: *\nDisallow: /\n'
    : `User-agent: *\nAllow: /\nSitemap: https://kingson4wu.github.io${withBase('/sitemap.xml', base)}\n`,
);
write(
  '404.html',
  `<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Page not found</title><body><h1>找不到这一页 / Page not found</h1><p><a href="${withBase('/zh-Hans/', base)}">返回全书目录 / Back to the book</a></p></body></html>`,
);
console.log(
  `Assembled ${locales.length} editions and ${pages.length} legacy links.`,
);
