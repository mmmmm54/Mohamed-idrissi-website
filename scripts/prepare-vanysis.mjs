import fs from 'node:fs/promises';
import sharp from 'sharp';
import groups from '../src/data/vanysis-work.json' with {type:'json'};
const dest='public/projects/vanysis/selected';
await fs.mkdir(`${dest}/web`,{recursive:true});
const dimensions={};
for(const file of groups.flatMap(group=>group.files)) {
 const source=`E:/Brands/Vanysis/${file}`;
 const meta=await sharp(source).metadata();
 await fs.copyFile(source,`${dest}/${file}`);
 // Trim only empty alpha padding; keep every visible artwork pixel.
 let pipeline=sharp(source).rotate();
 if(meta.hasAlpha) {
  const {data,info}=await sharp(source).ensureAlpha().raw().toBuffer({resolveWithObject:true});
  let left=info.width,top=info.height,right=-1,bottom=-1;
  for(let y=0;y<info.height;y++) for(let x=0;x<info.width;x++) {
   if(data[(y*info.width+x)*info.channels+info.channels-1]>0) {
    left=Math.min(left,x);right=Math.max(right,x);top=Math.min(top,y);bottom=Math.max(bottom,y);
   }
  }
  if(right>=left) pipeline=pipeline.extract({left,top,width:right-left+1,height:bottom-top+1});
 }
 const preview=await pipeline.resize({width:meta.width>meta.height?2400:1200,withoutEnlargement:true}).webp({quality:85}).toFile(`${dest}/web/${file}.webp`);
 dimensions[file]={width:preview.width,height:preview.height};
}
await fs.writeFile('src/data/vanysis-dimensions.json',JSON.stringify(dimensions,null,2));
console.log(`${Object.keys(dimensions).length} originals and optimized previews prepared.`);
