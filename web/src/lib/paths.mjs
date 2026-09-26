import path from 'node:path';
export function withBase(value, base = '/') {
  if (!value.startsWith('/') || value.startsWith('//')) return value;
  return `${base.replace(/\/$/, '')}${value}`;
}
export const chapterUrl = (locale, id, base = '/') =>
  withBase(`/${locale}/read/${id}/`, base);
export function resolveContentLink(url, source, pages, locale, base = '/') {
  if (/^(?:[a-z][a-z\d+.-]*:|#|\/\/)/i.test(url)) return url;
  const [target, hash] = url.split('#');
  const resolved = path.posix.normalize(
    path.posix.join(path.posix.dirname(source), decodeURI(target)),
  );
  const match = pages.find(
    (p) => p.path.replace(/\.md$/, '') === resolved.replace(/\.(md|html)$/, ''),
  );
  if (match)
    return chapterUrl(locale, match.id, base) + (hash ? '#' + hash : '');
  if (/\.(png|svg|jpg|jpeg|webp|gif)$/i.test(resolved))
    return withBase('/' + resolved, base);
  throw new Error(`Unknown book link ${url} from ${source}`);
}
