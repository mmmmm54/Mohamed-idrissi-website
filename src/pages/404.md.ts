import type { APIRoute } from 'astro';
import { SITE_URL } from '../lib/site';

/*
  The "page not found" body for agents that send "Accept: text/markdown".
  vercel.json serves it with status 404 for any path that does not exist.
*/
export const GET: APIRoute = ({ site }) => {
  const base = site ?? new URL(SITE_URL);
  const url = (path: string) => new URL(path, base).href;
  const body = `# 404 — Page not found

There is no page at this address on Mohamed Idrissi’s portfolio. The link may be old or mistyped.

Where to go instead:

- [Homepage](${url('/')}): selected work, services and contact
- [Sitemap](${url('/sitemap.xml')}): every page on the site
- [llms.txt](${url('/llms.txt')}): a plain-text guide to the site for AI agents
- [Contact](${url('/contact/')}): email or WhatsApp Mohamed directly
`;
  return new Response(body, { headers: { 'Content-Type': 'text/markdown; charset=utf-8' } });
};
