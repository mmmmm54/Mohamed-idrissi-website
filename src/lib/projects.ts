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

/* Full-width, then two side by side, repeating. */
export const isWideAt = (index: number) => index % 3 === 0;

export const isTodo = (value: string) => /^todo/i.test(value.trim());
