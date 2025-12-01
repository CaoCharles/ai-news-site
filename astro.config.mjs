import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

// https://astro.build/config
export default defineConfig({
    site: 'https://CaoCharles.github.io',
    base: '/ai-news-site/',
    integrations: [tailwind()],
});
