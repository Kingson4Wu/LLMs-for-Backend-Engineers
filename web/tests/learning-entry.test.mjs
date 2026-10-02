import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';


test('downloads present the specific AI learning routes', async () => {
  const downloads = await readFile(
    new URL('../src/pages/[locale]/downloads.astro', import.meta.url),
    'utf8',
  );
  assert.match(downloads, /Codex/);
  assert.match(downloads, /ChatGPT/);
  assert.match(downloads, /<pre tabindex="0"/);
});

test('reader styles retain accessible contrast and touch targets', async () => {
  const styles = await readFile(new URL('../src/styles/site.css', import.meta.url), 'utf8');
  assert.match(styles, /--muted:\s*#606a61/);
  assert.match(styles, /\.part-section h3 a\s*\{[^}]*min-height:\s*24px/s);
});

test('homepage has one tool-neutral learning action that stays inside the reader', async () => {
  const home = await readFile(new URL('../src/components/Home.astro', import.meta.url), 'utf8');
  assert.match(home, /AI 辅助学习/);
  assert.match(home, /Learn with AI/);
  assert.match(home, /chapterUrl\(locale, 'ai-learning-guide', base\)/);
  assert.doesNotMatch(home, /blob\/main\/learning/);
  assert.doesNotMatch(home, /用 Codex 学习/);
  assert.doesNotMatch(home, /用 ChatGPT 学习/);
});

test('homepage states the broader software-engineering audience without hiding the backend focus', async () => {
  const home = await readFile(new URL('../src/components/Home.astro', import.meta.url), 'utf8');
  assert.match(home, /AI 应用与平台工程师/);
  assert.match(home, /backend, AI application, and platform engineers/);
});

test('homepage uses the public title for software engineers', async () => {
  const home = await readFile(new URL('../src/components/Home.astro', import.meta.url), 'utf8');
  assert.match(home, /理解大模型：面向软件工程师的原理与系统指南/);
  assert.match(home, /Understanding LLMs for Software Engineers/);
});

test('reader watermark is decorative and cannot interfere with reading controls', async () => {
  const layout = await readFile(new URL('../src/layouts/Layout.astro', import.meta.url), 'utf8');
  const styles = await readFile(new URL('../src/styles/site.css', import.meta.url), 'utf8');
  assert.match(layout, /class="reading-watermark"/);
  assert.match(layout, /aria-hidden="true"/);
  assert.match(styles, /\.reading-watermark/);
  assert.match(styles, /pointer-events:\s*none/);
});

test('root homepage renders English without a redirect', async () => {
  const root = await readFile(new URL('../src/pages/index.astro', import.meta.url), 'utf8');
  assert.match(root, /<Home locale="en"\s*\/>/);
  assert.doesNotMatch(root, /zh-Hans/);
  assert.doesNotMatch(root, /redirect|location\./i);
});

test('download guidance presents Markdown as an AI-friendly edition', async () => {
  const downloads = await readFile(
    new URL('../src/pages/[locale]/downloads.astro', import.meta.url),
    'utf8',
  );
  assert.match(downloads, /ext: 'md'/);
  assert.match(downloads, /完整单文件书稿/);
  assert.match(downloads, /complete single-file manuscript/);
});

test('AI learning appendices expose a copyable tool-neutral starter prompt', async () => {
  const [zh, en] = await Promise.all([
    readFile(
      new URL('../../book/chapters/appendices/ai-learning-guide.md', import.meta.url),
      'utf8',
    ),
    readFile(
      new URL('../../book/translations/en/chapters/appendices/ai-learning-guide.md', import.meta.url),
      'utf8',
    ),
  ]);
  assert.match(zh, /可直接复制的学习提示词/);
  assert.match(en, /Copyable Starter Prompt/);
  assert.match(zh, /书中证据/);
  assert.match(en, /book evidence/);
  assert.match(zh, /若无法下载或读取该文件，请明确告诉我，并让我上传同语言书稿/);
  assert.match(en, /If you cannot download or read that file, tell me clearly and ask me to upload the same-language edition/);
});

test('homepage exposes one visible prompt for a deployed Markdown manuscript', async () => {
  const home = await readFile(
    new URL('../src/components/Home.astro', import.meta.url),
    'utf8',
  );
  assert.match(home, /learningPrompt/);
  assert.match(home, /exported\/\$\{locale\}\/Understanding-LLMs\.md/);
  assert.doesNotMatch(home, /Understanding-LLMs\.pdf/);
  assert.match(home, /data-copy-text/);
  assert.match(home, /让 AI 下载完整书稿/);
  assert.match(home, /Let AI download the complete book/);
  assert.match(home, /若无法下载或读取该文件，请明确告诉我，并让我上传同语言书稿/);
  assert.match(home, /If you cannot download or read that file, tell me clearly and ask me to upload the same-language edition/);
  assert.doesNotMatch(home, /uploadPrompt/);
});

test('postbuild publishes machine-discoverable AI learning materials', async () => {
  const postbuild = await readFile(new URL('../scripts/postbuild.mjs', import.meta.url), 'utf8');
  assert.match(postbuild, /llms\.txt/);
  assert.match(postbuild, /ai-learning\/index\.json/);
  assert.match(postbuild, /AI_ENTRY\.zh-Hans\.md/);
  assert.match(postbuild, /AI_ENTRY\.en\.md/);
  assert.match(postbuild, /LEARNING_CONTRACT\.zh-Hans\.md/);
  assert.match(postbuild, /LEARNING_CONTRACT\.en\.md/);
});

test('deployment validation requires the AI learning materials', async () => {
  const deploymentCheck = await readFile(
    new URL('../scripts/check-deployment.mjs', import.meta.url),
    'utf8',
  );
  assert.match(deploymentCheck, /llms\.txt/);
  assert.match(deploymentCheck, /ai-learning\/index\.json/);
  assert.match(deploymentCheck, /ai-learning\/en\.md/);
  assert.match(deploymentCheck, /ai-learning\/zh-Hans\.md/);
});

test('AI learning entries give each language a complete and traceable source route', async () => {
  const [zh, en] = await Promise.all([
    readFile(new URL('../../learning/AI_ENTRY.zh-Hans.md', import.meta.url), 'utf8'),
    readFile(new URL('../../learning/AI_ENTRY.en.md', import.meta.url), 'utf8'),
  ]);
  assert.match(zh, /完整单文件 Markdown/);
  assert.match(zh, /学习索引/);
  assert.match(zh, /书中证据/);
  assert.match(en, /complete single-file Markdown/);
  assert.match(en, /Learning index/);
  assert.match(en, /book evidence/);
});
