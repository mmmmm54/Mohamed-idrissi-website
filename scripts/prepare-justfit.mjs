import sharp from 'sharp';
import { readdir, mkdir } from 'node:fs/promises';
const base = 'public/projects/justfit/selected';
await mkdir(`${base}/web`, { recursive:true });
for (const file of await readdir(base)) {
  if (!file.endsWith('.jpg')) continue;
  await sharp(`${base}/${file}`).resize({width:1000,withoutEnlargement:true}).webp({quality:84}).toFile(`${base}/web/${file}.webp`);
}
