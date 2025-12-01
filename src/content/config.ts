import { defineCollection, z } from 'astro:content';

const posts = defineCollection({
    type: 'content',
    // Type-check frontmatter using a schema
    schema: z.object({
        title: z.string(),
        date: z.coerce.date(),
        category: z.enum(["World", "Business", "Technology", "Health", "Sports", "Culture", "Podcast"]),
        source: z.enum(["Google", "OpenAI", "Anthropic", "Mixed"]),
        tags: z.array(z.string()),
        summary: z.string(),
        heroImage: z.string().optional(),
        readingTime: z.string().optional(),
    }),
});

export const collections = { posts };
