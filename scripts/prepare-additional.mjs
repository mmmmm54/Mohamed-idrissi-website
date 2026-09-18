import fs from 'node:fs/promises';
import path from 'node:path';
import sharp from 'sharp';
import projects from '../src/data/additional-work.json' with {type:'json'};
const sizes={};
for(const [slug,project] of Object.entries(projects)) {
 for(const file of project.groups.flatMap(g=>g.files)) {
  const source=`${project.source}/${file}`;
  const dest=`public/projects/${slug}/selected/${file}`;
  const preview=`public/projects/${slug}/selected/web/${file}.webp`;
  await fs.mkdir(path.dirname(dest),{recursive:true});
  await fs.mkdir(path.dirname(preview),{recursive:true});
  await fs.copyFile(source,dest);
  const info=await sharp(source).rotate().resize({width:1200,withoutEnlargement:true}).webp({quality:85}).toFile(preview);
  sizes[`${slug}/${file}`]={width:info.width,height:info.height};
 }
}
await fs.writeFile('src/data/additional-dimensions.json',JSON.stringify(sizes,null,2));
await fs.copyFile('C:/Users/Setup Game/Downloads/SVG/Asset 1.svg','public/images/clients/dr-majed-mikhail.svg');
console.log(`Prepared ${Object.keys(sizes).length} artworks and the supplied doctor logo.`);
