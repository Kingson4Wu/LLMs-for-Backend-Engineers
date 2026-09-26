import { unified } from 'unified';
import parse from 'remark-parse';
import gfm from 'remark-gfm';
import math from 'remark-math';
import rehype from 'remark-rehype';
import katex from 'rehype-katex';
import slug from 'rehype-slug';
import highlight from 'rehype-highlight';
import stringify from 'rehype-stringify';
import legacySlug from 'github-slugid';
import { resolveContentLink } from './paths.mjs';

// A heading may be renamed when a chapter is restored or clarified. Keep only
// published bookmarks here so old shared links continue to land on the topic.
const historicalHeadingAliases = {
  softmax: {
    '1-问题设定从-logits-到概率': ['从分数到概率：四步走'],
    '从-logits-到概率问题设定': ['从分数到概率：四步走'],
  },
};
function walk(node, visit) {
  visit(node);
  for (const child of node.children ?? []) walk(child, visit);
}
function text(node) {
  return node.value ?? (node.children ?? []).map(text).join('');
}
export async function renderMarkdown(source, page, pages, locale, base) {
  const headings = [];
  let titleAlias;
  const adapt = () => (tree) => {
    if (tree.children[0]?.type === 'heading' && tree.children[0].depth === 1) {
      titleAlias = legacySlug(text(tree.children.shift()));
    }
    walk(tree, (n) => {
      if (n.type === 'link' || n.type === 'image')
        n.url = resolveContentLink(n.url, page.path, pages, locale, base);
    });
  };
  const outline = () => (tree) =>
    walk(tree, (n) => {
      if (n.type === 'element' && /^h[23]$/.test(n.tagName))
        headings.push({
          id: n.properties.id,
          text: text(n),
          depth: Number(n.tagName[1]),
        });
    });
  const aliases = () => (tree) => {
    const used = new Set();
    walk(tree, (n) => {
      if (n.properties?.id) used.add(n.properties.id);
    });
    const alias = (id) => ({
      type: 'element',
      tagName: 'span',
      properties: { id, className: ['legacy-anchor'], 'aria-hidden': 'true' },
      children: [],
    });
    const insert = (node) => {
      if (!node.children) return;
      node.children = node.children.flatMap((child) => {
        insert(child);
        if (child.type === 'element' && /^h[1-6]$/.test(child.tagName)) {
          const id = legacySlug(text(child));
          const historical = historicalHeadingAliases[page.id]?.[child.properties.id] ?? [];
          const aliases = [id, ...historical].filter((aliasId) => aliasId && !used.has(aliasId));
          for (const aliasId of aliases) used.add(aliasId);
          if (aliases.length) return [...aliases.map(alias), child];
        }
        return [child];
      });
    };
    insert(tree);
    if (titleAlias && !used.has(titleAlias))
      tree.children.unshift(alias(titleAlias));
  };
  const result = await unified()
    .use(parse)
    .use(gfm)
    .use(math)
    .use(adapt)
    .use(rehype)
    .use(slug)
    .use(aliases)
    .use(katex, { strict: false })
    .use(highlight, { detect: false })
    .use(outline)
    .use(stringify)
    .process(source);
  return { html: String(result), headings };
}
