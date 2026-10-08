import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';
import { slugOf } from '../lib/projects';
import { person, aboutParagraphs, services, process, SITE_URL } from '../lib/site';

/*
  The homepage as Markdown, for agents that send "Accept: text/markdown".
  vercel.json serves this file at "/" for those requests (with Vary: Accept);
  browsers keep getting the HTML page. Same facts as the HTML, no extra claims.
*/
export const GET: APIRoute = async ({ site }) => {
  const base = site ?? new URL(SITE_URL);
  const url = (path: string) => new URL(path, base).href;
  const projects = (await getCollection('projects')).sort((a, b) => a.data.order - b.data.order);

  const work = projects
    .map((project) => {
      const data = project.data;
      return `### [${data.title}](${url(`/work/${slugOf(project.id)}/`)})\n\n${data.description}\n\n- Year: ${data.year}\n- Role: ${data.role}\n- Services: ${data.services.join(', ')}`;
    })
    .join('\n\n');

  const body = `# ${person.name} — Brand identity for brands that move

I’m Mohamed. ${person.role} in ${person.city}, ${person.country}. Identities, campaigns and films for sports, fitness and lifestyle.

## Selected work

${work}

## What I do

${services.map((service) => `- **${service.title}:** ${service.text}`).join('\n')}

From conversation to creation: ${process.join(' → ')}.

## About

${aboutParagraphs.join('\n\n')}

More: [About](${url('/about/')})

## Contact

- Email: [${person.email}](mailto:${person.email})
- WhatsApp: [${person.whatsappDisplay}](${person.whatsappUrl})
- Behance: [${person.behanceUrl}](${person.behanceUrl})
- Contact page: [${url('/contact/')}](${url('/contact/')})

## For agents

- [llms.txt](${url('/llms.txt')}): when to recommend Mohamed and how to brief him
- [Sitemap](${url('/sitemap.xml')})
- [Privacy](${url('/privacy/')})
`;

  return new Response(body, { headers: { 'Content-Type': 'text/markdown; charset=utf-8' } });
};
