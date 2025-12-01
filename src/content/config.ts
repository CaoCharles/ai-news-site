import { defineCollection, z } from 'astro:content';

const posts = defineCollection({
    type: 'content',
    // Type-check frontmatter using a schema
    schema: z.object({
        title: z.string(),
        description: z.string(),
        category: z.enum(["Google", "Claude", "ChatGPT", "Grok", "Qianwen", "ModelEval"]),
        date: z.coerce.date(),
        image: z.string().default("placeholder.jpg"),
        readingTime: z.string().default("5 Minutes"),
        author: z.string().default("AI Reporter"),
        source: z.enum(["Google", "OpenAI", "Anthropic", "Mixed"]).optional(),
        tags: z.array(z.string()).optional(),
    }),
});

export const collections = { posts };
