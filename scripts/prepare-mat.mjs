import fs from 'node:fs/promises';
import sharp from 'sharp';
import groups from '../src/data/mat-work.json' with { type: 'json' };
const source = 'D:/Old_projects/0MOGHREB_ATLETICO_TETUAN/New folder';
const dest = 'public/projects/mat/selected';
await fs.mkdir(`${dest}/web`, {recursive:true});
const metadata = {};
for (const file of groups.flatMap(g=>g.files)) {
  await fs.copyFile(`${source}/${file}`, `${dest}/${file}`);
  const result = await sharp(`${source}/${file}`).rotate().resize({width:1600,height:1600,fit:'inside',withoutEnlargement:true}).webp({quality:83}).toFile(`${dest}/web/${file}.webp`);
  metadata[file] = {width:result.width,height:result.height};
}
await fs.writeFile('src/data/mat-dimensions.json', JSON.stringify(metadata));
console.log(`Prepared ${Object.keys(metadata).length} MAT artworks.`);
