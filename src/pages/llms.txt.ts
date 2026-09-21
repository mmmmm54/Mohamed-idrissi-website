import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';
import { slugOf } from '../lib/projects';

/* A plain-text summary for AI assistants and answer engines (llmstxt.org). Facts from the site only. */
export const GET: APIRoute = async ({ site }) => {
  const base = site ?? new URL('https://mohamedidrissi.site');
  const projects = (await getCollection('projects')).sort((a, b) => a.data.order - b.data.order);
  const work = projects
    .map((project) => `- [${project.data.title}](${new URL(`/work/${slugOf(project.id)}/`, base).href}): ${project.data.summary}`)
    .join('\n');
  const body = `# Mohamed Idrissi

> Graphic designer and creative director in Tétouan, Morocco, with 6 years of experience in sports, fitness and lifestyle branding. Brand identity, social media campaigns and video.

## Services

- Brand identity: strategy, logos, typography, colour and guidelines.
- Art direction: campaign concepts, editorial direction and social media systems.
- Creative production: AI-assisted imagery, cinematic films and video editing.

## Selected work

${work}

## Contact

- Website: ${base.href}
- Email: mohamedidrissi205@gmail.com
- WhatsApp: +212 691 865 970
- Behance: https://www.behance.net/Mohamed_Idrissi
`;
  return new Response(body, { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
};
