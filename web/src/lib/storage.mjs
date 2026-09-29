export function parsePosition(raw, key) {
  try {
    const p = JSON.parse(raw);
    const validProgress =
      (p?.version === 1 || p?.version === 2) &&
      p.key === key &&
      Number.isFinite(p.progress) &&
      p.progress >= 0 &&
      p.progress <= 1;
    if (!validProgress) return null;
    if (p.version === 1) return p;
    if (
      typeof p.section !== 'string' ||
      !p.section ||
      p.section.length > 200 ||
      /[<>\u0000-\u001f]/.test(p.section) ||
      (p.sectionTitle !== undefined &&
        (typeof p.sectionTitle !== 'string' ||
          p.sectionTitle.length > 500 ||
          /[\u0000-\u001f]/.test(p.sectionTitle)))
    )
      return null;
    return p;
  } catch {
    return null;
  }
}
export function parseBackup(raw, key) {
  const data = JSON.parse(raw);
  if (data?.version !== 1 || data.key !== key)
    throw new Error('Wrong edition or chapter');
  if (!Array.isArray(data.notes) || data.notes.length > 1000)
    throw new Error('Invalid notes');
  const ids = new Set();
  return data.notes.map((n) => {
    if (
      !n ||
      typeof n.id !== 'string' ||
      !n.id ||
      n.id.length > 100 ||
      ids.has(n.id) ||
      typeof n.quote !== 'string' ||
      n.quote.length > 10000 ||
      typeof n.note !== 'string' ||
      n.note.length > 20000 ||
      !Number.isFinite(n.createdAt) ||
      n.createdAt < 0
    )
      throw new Error('Invalid note');
    let anchor;
    if (n.anchor !== undefined) {
      if (
        !n.anchor ||
        typeof n.anchor !== 'object' ||
        (n.anchor.section !== undefined &&
          (typeof n.anchor.section !== 'string' ||
            n.anchor.section.length > 200 ||
            /[<>\u0000-\u001f]/.test(n.anchor.section))) ||
        typeof n.anchor.prefix !== 'string' ||
        n.anchor.prefix.length > 200 ||
        typeof n.anchor.suffix !== 'string' ||
        n.anchor.suffix.length > 200
      )
        throw new Error('Invalid note anchor');
      anchor = {
        ...(n.anchor.section ? { section: n.anchor.section } : {}),
        prefix: n.anchor.prefix,
        suffix: n.anchor.suffix,
      };
    }
    ids.add(n.id);
    return {
      id: n.id,
      quote: n.quote,
      note: n.note,
      createdAt: n.createdAt,
      ...(anchor ? { anchor } : {}),
    };
  });
}

export function findQuote(text, quote, anchor) {
  if (!quote) return null;
  const matches = [];
  let start = text.indexOf(quote);
  while (start >= 0) {
    const end = start + quote.length;
    const prefixMatches = !anchor?.prefix || text.slice(0, start).endsWith(anchor.prefix);
    const suffixMatches = !anchor?.suffix || text.slice(end).startsWith(anchor.suffix);
    if (prefixMatches && suffixMatches) matches.push({ start, end });
    start = text.indexOf(quote, start + 1);
  }
  return matches.length === 1 ? matches[0] : null;
}
