/** @type {import('tailwindcss').Config} */
export default {
    content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
    theme: {
        extend: {
            colors: {
                'news-black': '#1a1a1a',
                'news-gray': '#f4f4f4',
                'news-accent': '#d93025', // A standard news red
            },
            fontFamily: {
                serif: ['Merriweather', 'serif'],
                sans: ['Inter', 'sans-serif'],
            }
        },
    },
    plugins: [],
}
