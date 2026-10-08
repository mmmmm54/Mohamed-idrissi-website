/*
  Homepage cards ship only their first posters as <img> tags. The rest travel as
  one compact attribute, so a card with 40 posters adds one line of HTML, not 40
  image tags. Paths are already URL-encoded and contain no "|".
*/

export const QUEUE_SEPARATOR = '|';

/* Build time: turn full poster URLs into a shared base plus a short list. */
export function packQueue(urls: string[], base: string): string {
  return urls
    .map((url) => {
      if (!url.startsWith(base)) throw new Error(`Poster ${url} is outside ${base}`);
      const rest = url.slice(base.length);
      if (rest.includes(QUEUE_SEPARATOR)) throw new Error(`Poster path contains "${QUEUE_SEPARATOR}": ${url}`);
      return rest;
    })
    .join(QUEUE_SEPARATOR);
}

/* In the browser: the full URLs again, in order. */
export function unpackQueue(packed: string | undefined, base: string): string[] {
  return (packed || '').split(QUEUE_SEPARATOR).filter(Boolean).map((rest) => base + rest);
}
