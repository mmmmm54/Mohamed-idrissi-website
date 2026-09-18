import fs from 'node:fs/promises';
import sharp from 'sharp';
import projects from '../src/data/curated-work.json' with {type:'json'};
for (const [slug,project] of Object.entries(projects)) {
 const dest=`public/projects/${slug}/selected`;
 await fs.mkdir(`${dest}/web`,{recursive:true});
 for(const file of project.groups.flatMap(g=>g.files)) {
  await fs.copyFile(`${project.source}/${file}`,`${dest}/${file}`);
  await sharp(`${project.source}/${file}`).rotate().resize({width:1200,withoutEnlargement:true}).webp({quality:85}).toFile(`${dest}/web/${file}.webp`);
 }
 console.log(`${slug}: 9 originals and previews prepared`);
}
