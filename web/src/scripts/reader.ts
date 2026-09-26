import { parseBackup, parsePosition, findQuote } from '../lib/storage.mjs';
const grid = document.querySelector<HTMLElement>('.reader-grid');
const locale = grid.dataset.locale,
  key = `${locale}:${grid.dataset.chapter}`;
const english = locale === 'en',
  msg = (zh: string, en: string) => (english ? en : zh);
const article = document.querySelector<HTMLElement>('#article');
const byId = <T extends HTMLElement = HTMLElement>(id: string) =>
  document.getElementById(id) as T;
const toolbar = document.querySelector<HTMLElement>('.reader-toolbar');
toolbar.hidden = false;
const storageKey = `llms-position:${key}`;
let previous = null;
try {
  previous = parsePosition(localStorage.getItem(storageKey), key);
} catch {}
if (previous && previous.progress > 0.02 && previous.progress < 0.98) {
  byId('resume').hidden = false;
  if (previous.sectionTitle) {
    byId('resume-label').textContent = msg(
      `上次读到：${previous.sectionTitle}`,
      `Last read: ${previous.sectionTitle}`,
    );
  }
  byId('resume-button').onclick = () => {
    const section = previous.section && document.getElementById(previous.section);
    if (section && article.contains(section)) {
      section.scrollIntoView({ block: 'start', behavior: 'smooth' });
      byId('resume').hidden = true;
      return;
    }
    const top = article.getBoundingClientRect().top + scrollY;
    scrollTo({
      top:
        top +
        previous.progress * Math.max(0, article.offsetHeight - innerHeight / 2),
      behavior: 'smooth',
    });
    byId('resume').hidden = true;
  };
}
byId('resume-dismiss').onclick = () => (byId('resume').hidden = true);
let timer: ReturnType<typeof setTimeout>;
let latestProgress = 0;
const sectionHeadings = Array.from(
  article.querySelectorAll<HTMLElement>('h2[id], h3[id]'),
);
function currentSection() {
  const marker = innerHeight * 0.35;
  return sectionHeadings.reduce<HTMLElement | null>(
    (active, heading) => (heading.getBoundingClientRect().top <= marker ? heading : active),
    null,
  );
}
function savePosition() {
  try {
    const section = currentSection();
    localStorage.setItem(
      storageKey,
      JSON.stringify({
        version: 2,
        key,
        progress: latestProgress,
        section: section?.id ?? 'article-start',
        sectionTitle: section?.textContent?.trim() ?? msg('文章开头', 'Article start'),
      }),
    );
    localStorage.setItem(
      `llms-last:${locale}`,
      JSON.stringify({ href: location.href.split('#')[0] }),
    );
  } catch {}
}
function progress() {
  const top = article.getBoundingClientRect().top + scrollY;
  const p = Math.max(
    0,
    Math.min(
      1,
      (scrollY - top) / Math.max(1, article.offsetHeight - innerHeight / 2),
    ),
  );
  latestProgress = p;
  byId('progress-bar').style.width = `${p * 100}%`;
  clearTimeout(timer);
  timer = setTimeout(savePosition, 250);
}
addEventListener('scroll', progress, { passive: true });
addEventListener('pagehide', savePosition);
let fontSize = 18;
try {
  const saved = Number(localStorage.getItem('llms-font'));
  if (saved >= 15 && saved <= 24) fontSize = saved;
} catch {}
const font = () => {
  document.documentElement.style.setProperty('--reading-size', fontSize + 'px');
  try {
    localStorage.setItem('llms-font', String(fontSize));
  } catch {}
};
font();
byId('smaller').onclick = () => {
  fontSize = Math.max(15, fontSize - 1);
  font();
};
byId('larger').onclick = () => {
  fontSize = Math.min(24, fontSize + 1);
  font();
};
byId('focus').onclick = () => {
  const active = document.body.classList.toggle('focused');
  byId('focus').setAttribute('aria-pressed', String(active));
};
const nav = byId<HTMLDetailsElement>('book-navigation');
if (matchMedia('(max-width: 900px)').matches) nav.open = false;
article.querySelectorAll('pre').forEach((pre) => {
  const button = document.createElement('button');
  button.className = 'copy-code';
  button.textContent = msg('复制', 'Copy');
  button.onclick = async () => {
    try {
      await navigator.clipboard.writeText(
        pre.querySelector('code')?.textContent ?? '',
      );
      button.textContent = msg('已复制', 'Copied');
    } catch {
      button.textContent = msg('请手动选择复制', 'Select and copy manually');
    }
    setTimeout(() => (button.textContent = msg('复制', 'Copy')), 1800);
  };
  pre.append(button);
});
document.querySelectorAll<HTMLDialogElement>('dialog').forEach((dialog) => {
  dialog.querySelector<HTMLButtonElement>('[data-close]').onclick = () =>
    dialog.close();
  dialog.addEventListener('click', (e) => {
    if (e.target === dialog) {
      const r = dialog.getBoundingClientRect();
      if (
        e.clientX < r.left ||
        e.clientX > r.right ||
        e.clientY < r.top ||
        e.clientY > r.bottom
      )
        dialog.close();
    }
  });
});
const search = byId<HTMLDialogElement>('search-dialog'),
  searchButton = byId<HTMLButtonElement>('search-open');
searchButton.hidden = false;
let searchReady = false;
async function openSearch() {
  search.showModal();
  if (searchReady) return;
  const config = (window as any).bookSearchConfig;
  const base = config.base.replace(/\/$/, '');
  try {
    const css = document.createElement('link');
    css.rel = 'stylesheet';
    css.href = base + '/pagefind/pagefind-ui.css';
    document.head.append(css);
    await new Promise<void>((resolve, reject) => {
      const script = document.createElement('script');
      script.src = base + '/pagefind/pagefind-ui.js';
      script.onload = () => resolve();
      script.onerror = reject;
      document.head.append(script);
    });
    new (window as any).PagefindUI({
      element: '#search',
      showSubResults: true,
      showImages: false,
      translations: english
        ? {}
        : {
            placeholder: '搜索关键词',
            zero_results: '未找到 [SEARCH_TERM] 的结果',
            search_label: '搜索全书',
            clear_search: '清除',
            load_more: '更多结果',
            searching: '正在搜索…',
          },
    });
    searchReady = true;
  } catch {
    byId('search').textContent = msg(
      '搜索索引不可用。请先构建网站后预览。',
      'Search index unavailable. Build the site before previewing.',
    );
  }
}
searchButton.onclick = openSearch;
addEventListener('keydown', (e) => {
  if (
    e.key === '/' &&
    !['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName) &&
    !document.querySelector('dialog[open]')
  ) {
    e.preventDefault();
    openSearch();
  }
});
const notesKey = `llms-notes:${key}`,
  dialog = byId<HTMLDialogElement>('notes-dialog');
let notes: Array<{
  id: string;
  quote: string;
  note: string;
  createdAt: number;
  anchor?: { section?: string; prefix: string; suffix: string };
}> = [];
try {
  const saved = localStorage.getItem(notesKey);
  if (saved) notes = parseBackup(saved, key);
} catch {
  byId('note-status').textContent = msg(
    '无法读取本地备份。原始数据尚未更改。',
    'Could not read the saved notes. Existing storage has not been changed.',
  );
}
let quote = '';
let selectionAnchor: { section?: string; prefix: string; suffix: string } | undefined;
function textNodes() {
  const walker = document.createTreeWalker(article, NodeFilter.SHOW_TEXT);
  const nodes: Text[] = [];
  while (walker.nextNode()) nodes.push(walker.currentNode as Text);
  return nodes;
}
function quoteRange(value: string, anchor?: typeof selectionAnchor): Range | null {
  const nodes = textNodes();
  const match = findQuote(nodes.map((n) => n.data).join(''), value, anchor);
  if (!match) return null;
  const range = document.createRange();
  let offset = 0,
    started = false;
  for (const node of nodes) {
    const end = offset + node.length;
    if (!started && match.start >= offset && match.start < end) {
      range.setStart(node, match.start - offset);
      started = true;
    }
    if (started && match.end <= end) {
      range.setEnd(node, match.end - offset);
      return range;
    }
    offset = end;
  }
  return null;
}
function anchorFor(range: Range) {
  const before = range.cloneRange();
  before.selectNodeContents(article);
  before.setEnd(range.startContainer, range.startOffset);
  const after = range.cloneRange();
  after.selectNodeContents(article);
  after.setStart(range.endContainer, range.endOffset);
  const section = sectionHeadings
    .filter(
      (heading) =>
        heading.compareDocumentPosition(range.startContainer) &
        Node.DOCUMENT_POSITION_FOLLOWING,
    )
    .at(-1);
  return {
    ...(section ? { section: section.id } : {}),
    prefix: before.toString().slice(-120),
    suffix: after.toString().slice(0, 120),
  };
}
function paintQuotes() {
  const api = (CSS as any).highlights,
    HighlightConstructor = (window as any).Highlight;
  if (!api || !HighlightConstructor) return;
  const ranges = notes.map((n) => quoteRange(n.quote, n.anchor)).filter(Boolean);
  api.set('book-notes', new HighlightConstructor(...ranges));
}
paintQuotes();
function renderNotes() {
  const list = byId('notes-list');
  list.replaceChildren();
  for (const n of notes) {
    const item = document.createElement('section');
    item.className = 'note';
    const excerpt = document.createElement('blockquote'),
      body = document.createElement('p'),
      remove = document.createElement('button');
    excerpt.textContent = n.quote;
    body.textContent = n.note;
    remove.textContent = msg('删除', 'Delete');
    remove.onclick = () => {
      const updated = notes.filter((x) => x.id !== n.id);
      if (persist(updated)) renderNotes();
    };
    item.append(excerpt, body, remove);
    if (n.quote) {
      const range = quoteRange(n.quote, n.anchor),
        locate = document.createElement('button');
      locate.textContent = range
        ? msg('回到原文', 'Locate passage')
        : msg(
            '原文已变更或有重复，无法精确定位',
            'Passage changed or is ambiguous',
          );
      locate.disabled = !range;
      locate.onclick = () => {
        dialog.close();
        range?.startContainer.parentElement?.scrollIntoView({
          block: 'center',
          behavior: 'smooth',
        });
      };
      item.append(locate);
    }
    list.append(item);
  }
}
function persist(updated: typeof notes) {
  try {
    localStorage.setItem(
      notesKey,
      JSON.stringify({ version: 1, key, notes: updated }),
    );
    notes = updated;
    paintQuotes();
    byId('note-status').textContent = msg(
      '已保存到本机。',
      'Saved in this browser.',
    );
    return true;
  } catch {
    byId('note-status').textContent = msg(
      '保存失败，请导出备份后检查浏览器存储。',
      'Could not save. Export a backup and check browser storage.',
    );
    return false;
  }
}
byId('notes-open').onclick = () => {
  const selection = getSelection();
  const selectedRange =
    selection &&
    article.contains(selection.anchorNode) &&
    article.contains(selection.focusNode)
      ? selection.getRangeAt(0)
      : null;
  quote = selectedRange?.toString().slice(0, 10000) ?? '';
  selectionAnchor = selectedRange && quote ? anchorFor(selectedRange) : undefined;
  byId('selected-quote').textContent = quote;
  renderNotes();
  dialog.showModal();
};
byId('save-note').onclick = () => {
  const input = byId<HTMLTextAreaElement>('note-text');
  if (!input.value.trim() && !quote) return;
  if (notes.length >= 1000) {
    byId('note-status').textContent = msg(
      '本篇笔记已达上限，请先导出。',
      'Note limit reached. Export your notes first.',
    );
    return;
  }
  if (
    persist([
      ...notes,
      {
        id: crypto.randomUUID(),
        quote,
        note: input.value,
        createdAt: Date.now(),
        ...(selectionAnchor ? { anchor: selectionAnchor } : {}),
      },
    ])
  ) {
    input.value = '';
    quote = '';
    selectionAnchor = undefined;
    byId('selected-quote').textContent = '';
    renderNotes();
  }
};
byId('export-notes').onclick = () => {
  const url = URL.createObjectURL(
    new Blob([JSON.stringify({ version: 1, key, notes }, null, 2)], {
      type: 'application/json',
    }),
  );
  const a = document.createElement('a');
  a.href = url;
  a.download = `llms-notes-${locale}-${grid.dataset.chapter}.json`;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
};
byId<HTMLInputElement>('import-notes').onchange = async (e) => {
  const input = e.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) return;
  try {
    if (file.size > 5_000_000) throw new Error();
    const imported = parseBackup(await file.text(), key);
    const existing = new Set(notes.map((n) => n.id));
    const merged = [...notes, ...imported.filter((n) => !existing.has(n.id))];
    if (merged.length > 1000) throw new Error();
    if (persist(merged)) renderNotes();
  } catch {
    byId('note-status').textContent = msg(
      '备份无效，或不属于当前语言和文章。',
      'Invalid backup, or a different edition/chapter.',
    );
  }
  input.value = '';
};
