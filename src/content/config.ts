import { defineCollection, z } from 'astro:content';

const projects = defineCollection({
  type: 'content',
  schema: z.object({
    /* Homepage card */
    title: z.string(),
    shortTitle: z.string().optional(),
    description: z.string(),
    kind: z.enum(['featured', 'small']),
    order: z.number(),
    metric: z.string(),

    /* Case study — hero */
    summary: z.string(),
    role: z.string(),
    year: z.string(),
    services: z.array(z.string()),

    /* Case study — body */
    challenge: z.array(z.string()),
    approach: z.array(z.string()),
    results: z.array(z.string()),
    galleryNotes: z.array(z.string()).default([]),
    deliverables: z.array(z.object({ title: z.string(), description: z.string() })).default([]),
    /* Optional editorial notebook: populated only where the project needs it. */
    notebook: z.object({
      headline: z.string(),
      intro: z.string(),
      image: z.string().optional(),
      imageLabel: z.string().optional(),
      notes: z.array(z.object({ title: z.string(), text: z.string() })),
    }).optional(),

    /* Optional film embeds (MAALEM) */
    films: z
      .array(
        z.object({
          title: z.string(),
          note: z.string().optional(),
          embed: z.string().optional(),
        })
      )
      .default([]),
  }),
});

export const collections = { projects };
