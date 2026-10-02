import fs from 'node:fs';
import path from 'node:path';
import { catalog, pages, locales, bookDir } from '../src/lib/book.mjs';
import { chapterUrl, withBase } from '../src/lib/paths.mjs';
const base = process.env.SITE_BASE ?? '/Understanding-LLMs/';
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
const learning = path.join(bookDir, '..', 'learning');
const siteUrl = (route) => `https://kingson4wu.github.io${withBase(route, base)}`;
const copyLearningFile = (source, target) => {
  const destination = new URL(target, dist);
  fs.mkdirSync(path.dirname(destination.pathname), { recursive: true });
  fs.copyFileSync(path.join(learning, source), destination);
};
if (fs.existsSync(exported)) {
  for (const locale of locales) {
    const dir = path.join(exported, locale);
    if (fs.existsSync(dir)) {
      fs.mkdirSync(new URL(`exported/${locale}/`, dist), { recursive: true });
      for (const file of [
        'Understanding-LLMs.pdf',
        'Understanding-LLMs.epub',
        'Understanding-LLMs.print.html',
        'Understanding-LLMs.md',
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
for (const [source, target] of [
  ['index.json', 'ai-learning/index.json'],
  ['AI_ENTRY.zh-Hans.md', 'ai-learning/zh-Hans.md'],
  ['AI_ENTRY.en.md', 'ai-learning/en.md'],
  ['LEARNING_CONTRACT.zh-Hans.md', 'ai-learning/zh-Hans/contract.md'],
  ['LEARNING_CONTRACT.en.md', 'ai-learning/en/contract.md'],
  ['BOOK_MAP.md', 'ai-learning/book-map.zh-Hans.md'],
]) copyLearningFile(source, target);
write(
  'llms.txt',
  `# Understanding LLMs for Software Engineers

> A systems-first book for engineers learning how language models learn, generate, connect to external systems, and run as dependable services.

## AI learning entries

- [English AI learning entry](${siteUrl('/ai-learning/en.md')})
- [简体中文 AI 学习入口](${siteUrl('/ai-learning/zh-Hans.md')})
- [Bilingual learning index](${siteUrl('/ai-learning/index.json')})

## Complete editions

- [English Markdown](${siteUrl('/exported/en/Understanding-LLMs.md')})
- [English EPUB](${siteUrl('/exported/en/Understanding-LLMs.epub')})
- [Simplified Chinese Markdown](${siteUrl('/exported/zh-Hans/Understanding-LLMs.md')})
- [Simplified Chinese EPUB](${siteUrl('/exported/zh-Hans/Understanding-LLMs.epub')})

Read the language-specific AI learning entry before tutoring. It specifies evidence boundaries, citation expectations, and the fallback when a file cannot be read.
`,
);
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
