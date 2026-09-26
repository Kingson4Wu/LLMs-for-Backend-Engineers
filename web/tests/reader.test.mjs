import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { withBase, chapterUrl, resolveContentLink } from '../src/lib/paths.mjs';
import {
  findQuote,
  parseBackup,
  parsePosition,
} from '../src/lib/storage.mjs';
import { renderMarkdown } from '../src/lib/markdown.mjs';
test('links stay in deployment base and resolve extensionless references', () => {
  const pages = [
    { id: 'softmax', path: 'chapters/part1/softmax.md' },
    { id: 'attention', path: 'chapters/part2/attention.md' },
  ];
  assert.equal(withBase('/en/', '/project/'), '/project/en/');
  assert.equal(
    chapterUrl('zh-Hans', 'softmax', '/project/'),
    '/project/zh-Hans/read/softmax/',
  );
  assert.equal(
    resolveContentLink(
      '../part2/attention#q',
      pages[0].path,
      pages,
      'en',
      '/project/',
    ),
    '/project/en/read/attention/#q',
  );
  assert.equal(
    resolveContentLink(
      'https://example.org',
      pages[0].path,
      pages,
      'en',
      '/project/',
    ),
    'https://example.org',
  );
  assert.throws(
    () => resolveContentLink('./missing', pages[0].path, pages, 'en', '/'),
    /Unknown/,
  );
});
test('note backups are edition scoped and validated as a whole', () => {
  const record = {
    id: 'a',
    quote: 'Hello',
    note: 'My note',
    createdAt: 1,
    anchor: { section: 'why-it-matters', prefix: 'Before ', suffix: ' world' },
  };
  assert.deepEqual(
    parseBackup(
      JSON.stringify({ version: 1, key: 'en:softmax', notes: [record] }),
      'en:softmax',
    ),
    [record],
  );
  assert.throws(
    () =>
      parseBackup(
        JSON.stringify({ version: 1, key: 'zh-Hans:softmax', notes: [] }),
        'en:softmax',
      ),
    /edition/,
  );
  assert.throws(
    () =>
      parseBackup(
        JSON.stringify({
          version: 1,
          key: 'en:softmax',
          notes: [{ ...record, note: 3 }],
        }),
        'en:softmax',
      ),
    /Invalid/,
  );
  assert.equal(parsePosition('{broken', 'en:softmax'), null);
  assert.equal(
    parsePosition(
      JSON.stringify({ version: 1, key: 'en:softmax', progress: 2 }),
      'en:softmax',
    ),
    null,
  );
});

test('reading positions restore a named section and remain compatible with saved progress', () => {
  assert.deepEqual(
    parsePosition(
      JSON.stringify({
        version: 2,
        key: 'en:softmax',
        progress: 0.4,
        section: 'why-it-matters',
        sectionTitle: 'Why it matters',
      }),
      'en:softmax',
    ),
    {
      version: 2,
      key: 'en:softmax',
      progress: 0.4,
      section: 'why-it-matters',
      sectionTitle: 'Why it matters',
    },
  );
  assert.deepEqual(
    parsePosition(
      JSON.stringify({ version: 1, key: 'en:softmax', progress: 0.4 }),
      'en:softmax',
    ),
    { version: 1, key: 'en:softmax', progress: 0.4 },
  );
  assert.equal(
    parsePosition(
      JSON.stringify({
        version: 2,
        key: 'en:softmax',
        progress: 0.4,
        section: '<bad>',
      }),
      'en:softmax',
    ),
    null,
  );
});
test('markdown renders math, headings and chapter links', async () => {
  const pages = [{ id: 'softmax', path: 'chapters/softmax.md' }];
  const result = await renderMarkdown(
    '# Title\n\n## 标题\n\nA $V$ matrix.\n\n[Read](./softmax#标题)\n\n```python\nprint(1)\n```',
    pages[0],
    pages,
    'zh-Hans',
    '/book/',
  );
  assert.ok(result.html.includes('katex'));
  assert.ok(result.html.includes('language-python'));
  assert.ok(result.html.includes('/book/zh-Hans/read/softmax/#'));
  assert.equal(result.headings[0].text, '标题');
  assert.ok(!result.html.includes('<h1'));
});

test('legacy Honkit heading aliases preserve punctuation and the old H1 bookmark', async () => {
  const page = { id: 'softmax', path: 'softmax.md' };
  const result = await renderMarkdown(
    '# Softmax：权重路由\n\n## 从分数到概率：四步走\n\nText',
    page,
    [page],
    'zh-Hans',
    '/',
  );
  assert.ok(result.html.includes('id="从分数到概率：四步走"'));
  assert.ok(result.html.includes('id="softmax：权重路由"'));
});

test('renamed Softmax heading preserves its historical bookmark', async () => {
  const page = { id: 'softmax', path: 'softmax.md' };
  const result = await renderMarkdown(
    '# Softmax：怎样把分数变成概率\n\n## 1. 问题设定：从 logits 到概率\n\nText',
    page,
    [page],
    'zh-Hans',
    '/',
  );
  assert.ok(result.html.includes('id="从分数到概率：四步走"'));
});

test('current Softmax heading preserves the same historical bookmark', async () => {
  const page = { id: 'softmax', path: 'softmax.md' };
  const result = await renderMarkdown(
    '# Softmax：怎样把分数变成概率\n\n## 从 logits 到概率：问题设定\n\nText',
    page,
    [page],
    'zh-Hans',
    '/',
  );
  assert.ok(result.html.includes('id="从分数到概率：四步走"'));
});

test('saved quotes relocate after edits but ambiguous or removed quotes stay unmatched', async () => {
  assert.deepEqual(findQuote('new prefix quoted text suffix', 'quoted text'), {
    start: 11,
    end: 22,
  });
  assert.equal(findQuote('same and same', 'same'), null);
  assert.equal(findQuote('different', 'missing'), null);
});

test('saved quote context resolves a repeated passage after an article revision', () => {
  const text = 'First shared passage. Before shared passage after. Last shared passage.';
  assert.deepEqual(
    findQuote(text, 'shared passage', { prefix: 'Before ', suffix: ' after' }),
    { start: 29, end: 43 },
  );
  assert.equal(
    findQuote(text, 'shared passage', { prefix: 'Missing ', suffix: ' after' }),
    null,
  );
});

test('reader source records section-aware progress and contextual note anchors', () => {
  const source = fs.readFileSync(path.resolve('src/scripts/reader.ts'), 'utf8');
  assert.match(source, /version: 2/);
  assert.match(source, /sectionTitle/);
  assert.match(source, /selectionAnchor/);
  assert.match(source, /addEventListener\('pagehide', savePosition\)/);
});

test('homepage uses an editorial reading note instead of an animated system map', () => {
  const component = fs.readFileSync(
    path.resolve('src/components/Home.astro'),
    'utf8',
  );
  assert.match(component, /hero-reading-note/);
  assert.match(component, /#contents/);
  assert.doesNotMatch(component, /KnowledgeMap/);
  assert.doesNotMatch(component, /data-map-stage/);
});

test('browser smoke covers the editorial home entry and keyboard entry', () => {
  const smoke = fs.readFileSync(path.resolve('scripts/browser-smoke.py'), 'utf8');
  assert.match(smoke, /hero-reading-note/);
  assert.match(smoke, /keyboard\.press\('Tab'\)/);
  assert.match(smoke, /saved_position\['version'\] == 2/);
  assert.match(smoke, /#resume-button/);
});
