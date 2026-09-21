import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';
import { slugOf } from '../lib/projects';

/* Every public page, rebuilt on each deploy. Submit /sitemap.xml in Google Search Console. */
export const GET: APIRoute = async ({ site }) => {
  const base = site ?? new URL('https://www.mohamedidrissi.site');
  const projects = await getCollection('projects');
  const paths = ['/', ...projects.map((project) => `/work/${slugOf(project.id)}/`)];
  const today = new Date().toISOString().slice(0, 10);
  const urls = paths
    .map((path) => `  <url><loc>${new URL(path, base).href}</loc><lastmod>${today}</lastmod><priority>${path === '/' ? '1.0' : '0.8'}</priority></url>`)
    .join('\n');
  return new Response(`<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}\n</urlset>\n`, {
    headers: { 'Content-Type': 'application/xml; charset=utf-8' },
  });
};
