import fs from 'node:fs';
import path from 'node:path';

/*
  Asset helpers.
  Everything lives in public/projects/<slug>/ so swapping a file is the only step:
    cover.jpg        the one cover image used on the card and the case study hero
    cover.mp4        optional looping video, used instead of the cover on the card
    01.jpg, 02.jpg…  the case study gallery, picked up in numeric order
*/

const PUBLIC_PROJECTS = path.join(process.cwd(), 'public', 'projects');
const GALLERY_FILE = /^\d{2}\.(jpe?g|png|webp)$/i;

export const slugOf = (id: string) => id.replace(/\.md$/, '');

export const coverOf = (slug: string) => `/projects/${slug}/cover.jpg`;

const fileExists = (slug: string, name: string) => fs.existsSync(path.join(PUBLIC_PROJECTS, slug, name));

export function loopVideoOf(slug: string): string | null {
  return fileExists(slug, 'cover.mp4') ? `/projects/${slug}/cover.mp4` : null;
}

export function galleryOf(slug: string, category?: 'identity' | 'social' | 'campaigns'): string[] {
  const dir = path.join(PUBLIC_PROJECTS, slug, category || '');
  if (!fs.existsSync(dir)) return [];
  return fs
    .readdirSync(dir)
    .filter((file) => GALLERY_FILE.test(file))
    .sort()
    .map((file) => `/projects/${slug}/${category ? category + '/' : ''}${file}`);
}

/*
  Posters shown on the homepage card, cycled one after another.
  Every file in selected/web/ is used. src/data/project-covers.json only sets
  which ones come first; the rest follow in file order. Posters load one at a
  time, just before each is shown, so the visitor never downloads the whole set
  at once.
*/
const POSTER_FILE = /\.(webp|png|jpe?g)$/i;

export function postersOf(slug: string, curated: string[] = []): string[] {
  const dir = path.join(PUBLIC_PROJECTS, slug, 'selected', 'web');
  if (!fs.existsSync(dir)) return [];
  const url = (name: string) =>
    `/projects/${slug}/selected/web/${name.split('/').map(encodeURIComponent).join('/')}`;
  const picked = curated.map((file) => `${file}.webp`).filter((name) => fs.existsSync(path.join(dir, name)));
  const rest = fs
    .readdirSync(dir)
    .filter((file) => POSTER_FILE.test(file) && !picked.includes(file))
    .sort();
  /* Cards are portrait: a wide photo or banner would be cropped to a blur, so it
     stays on the project page and is skipped here. */
  return [...picked, ...rest].filter((file) => !isLandscape(path.join(dir, file))).map(url);
}

/* Width and height straight from the file header (WebP, PNG, JPEG). No image library needed. */
function imageSize(file: string): { width: number; height: number } | null {
  const b = fs.readFileSync(file);
  if (b.toString('ascii', 0, 4) === 'RIFF' && b.toString('ascii', 8, 12) === 'WEBP') {
    const chunk = b.toString('ascii', 12, 16);
    if (chunk === 'VP8X') return { width: 1 + b.readUIntLE(24, 3), height: 1 + b.readUIntLE(27, 3) };
    if (chunk === 'VP8 ') return { width: b.readUInt16LE(26) & 0x3fff, height: b.readUInt16LE(28) & 0x3fff };
    if (chunk === 'VP8L') {
      const bits = b.readUInt32LE(21);
      return { width: (bits & 0x3fff) + 1, height: ((bits >> 14) & 0x3fff) + 1 };
    }
  }
  if (b.readUInt32BE(0) === 0x89504e47) return { width: b.readUInt32BE(16), height: b.readUInt32BE(20) };
  if (b[0] === 0xff && b[1] === 0xd8) {
    let i = 2;
    while (i < b.length - 9) {
      if (b[i] !== 0xff) { i += 1; continue; }
      const marker = b[i + 1];
      if (marker >= 0xc0 && marker <= 0xcf && ![0xc4, 0xc8, 0xcc].includes(marker)) {
        return { width: b.readUInt16BE(i + 7), height: b.readUInt16BE(i + 5) };
      }
      i += 2 + b.readUInt16BE(i + 2);
    }
  }
  return null;
}

const isLandscape = (file: string) => {
  const size = imageSize(file);
  return !!size && size.width > size.height * 1.05;
};

/* Each card runs at its own pace so the cards never flip together. */
export function posterHoldOf(slug: string): number {
  const spread = [...slug].reduce((sum, char, i) => sum + char.charCodeAt(0) * (i + 3), 0);
  return 4000 + (spread % 5) * 200;
}

/* Full-width, then two side by side, repeating. */
export const isWideAt = (index: number) => index % 3 === 0;

export const isTodo = (value: string) => /^todo/i.test(value.trim());
