import fs from 'node:fs';
import path from 'node:path';
export const bookDir = path.resolve(process.cwd(), '../book');
export const catalog = JSON.parse(
  fs.readFileSync(path.join(bookDir, 'catalog.json'), 'utf8'),
);
export const metadata = JSON.parse(
  fs.readFileSync(path.join(bookDir, 'book.json'), 'utf8'),
);
export const editions = JSON.parse(
  fs.readFileSync(path.join(bookDir, 'editions.json'), 'utf8'),
);
export const pages = [
  ...catalog.frontmatter,
  ...catalog.parts.flatMap((p) =>
    [
      { id: p.id, path: p.path, title: p.title, part: p.id, kind: 'part' },
      ...p.chapters.map((c) => ({ ...c, part: p.id })),
    ],
  ),
];
export const locales = Object.keys(editions.editions).filter(
  (l) => editions.editions[l].status === 'published',
);
export const repo = 'https://github.com/kingson4wu/LLMs-for-Backend-Engineers';
export function sourceFor(locale, page) {
  return fs.readFileSync(
    path.join(bookDir, editions.editions[locale].source, page.path),
    'utf8',
  );
}
export function titleFor(locale, page) {
  return sourceFor(locale, page).match(/^#\s+(.+)$/m)?.[1] ?? page.title;
}
export function minutes(source) {
  const cjk = (source.match(/[\u3400-\u9fff]/g) || []).length;
  return Math.max(
    1,
    Math.ceil(
      cjk / 400 +
        source.replace(/[\u3400-\u9fff]/g, '').split(/\s+/).length / 220,
    ),
  );
}
export const partTitle = (locale, part) =>
  locale === 'en'
    ? {
        'math-foundations': 'Math & machine learning',
        'llm-internal': 'LLM internals',
        'llm-external': 'LLMs and external systems',
        'serving-runtime': 'LLM infrastructure',
        appendices: 'Further reading',
        appendix: 'Appendix',
      }[part.id]
    : part.title;
export const partDescription = (locale, part) =>
  locale === 'en'
    ? {
        'llm-internal':
          'Capability formation and adaptation → representation and computation → generation and extension.',
        'llm-external':
          'Capability boundaries → context and evidence → tools, protocols, and skills → harnesses and Agent runtimes → evaluation loops.',
        'serving-runtime':
          'Requests and state → concurrency and capacity → model service and delivery.',
      }[part.id]
    : part.introduction;
export const partNumber = (locale, index) =>
  locale === 'en'
    ? index < 4
      ? 'Part ' + (index + 1)
      : ''
    : ['一、', '二、', '三、', '四、', '', ''][index];
export const chapterNumber = (index) => String(index + 1);
export const t = (locale, zh, en) => (locale === 'en' ? en : zh);
