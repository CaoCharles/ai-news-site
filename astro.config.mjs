import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

// https://astro.build/config
export default defineConfig({
    site: 'https://example.github.io', // Placeholder, should be updated by user
    base: '/ai-trends-site', // Placeholder, matches the repo name usually
    integrations: [tailwind()],
});
