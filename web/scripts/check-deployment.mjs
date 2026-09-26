import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
const root = path.resolve('dist'),
  base = process.env.SITE_BASE ?? '/LLMs-for-Backend-Engineers/';
const walk = (dir) =>
  fs
    .readdirSync(dir, { withFileTypes: true })
    .flatMap((e) =>
      e.isDirectory() ? walk(path.join(dir, e.name)) : [path.join(dir, e.name)],
    );
const files = walk(root),
  htmls = new Map(
    files
      .filter((f) => f.endsWith('.html'))
      .map((f) => [f, fs.readFileSync(f, 'utf8')]),
  );
const decode = (s) =>
  s.replaceAll('&amp;', '&').replaceAll('&#39;', "'").replaceAll('&quot;', '"');
let checked = 0;
for (const [file, html] of htmls) {
  const page = path.relative(root, file).replace(/index\.html$/, '');
  const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map((m) => decode(m[1]));
  assert.equal(ids.length, new Set(ids).size, `Duplicate IDs in ${page}`);
  for (const [tag] of html.matchAll(/<[a-z][\w-]*\b[^<>]*>/gi))
    for (const [, raw] of tag.matchAll(/\b(?:href|src)="([^"]+)"/g)) {
      if (/^(data:|mailto:|tel:|javascript:)/.test(raw)) continue;
      const url = new URL(decode(raw), `https://site.test${base}${page}`);
      if (url.origin !== 'https://site.test') continue;
      assert.ok(url.pathname.startsWith(base), `Escapes base: ${page}: ${raw}`);
      let target = path.join(
        root,
        decodeURIComponent(url.pathname.slice(base.length)),
      );
      assert.ok(fs.existsSync(target), `Missing resource: ${page}: ${raw}`);
      if (fs.statSync(target).isDirectory())
        target = path.join(target, 'index.html');
      assert.ok(fs.existsSync(target), `Missing index: ${raw}`);
      if (url.hash && htmls.has(target)) {
        const fragment = decodeURIComponent(url.hash.slice(1));
        assert.ok(
          [...htmls.get(target).matchAll(/\bid="([^"]+)"/g)].some(
            (m) => decode(m[1]) === fragment,
          ),
          `Missing anchor ${page}: ${raw}`,
        );
      }
      checked++;
    }
}
assert.ok(
  fs.existsSync(path.join(root, 'pagefind/pagefind.js')),
  'Missing search index',
);
console.log(
  `Checked ${htmls.size} pages and ${checked} local references under ${base}`,
);
