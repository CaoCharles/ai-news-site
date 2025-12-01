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
                serif: ['"Playfair Display"', 'Georgia', 'serif'],
                sans: ['"Microsoft JhengHei"', '"微軟正黑體"', '"Inter"', 'system-ui', 'sans-serif'],
            },
            typography: {
                DEFAULT: {
                    css: {
                        maxWidth: '100%',
                        lineHeight: '1.8',
                        p: {
                            marginBottom: '1.25em',
                        },
                        'h1, h2, h3, h4': {
                            fontWeight: '700',
                            marginTop: '1.5em',
                            marginBottom: '0.75em',
                        },
                        li: {
                            marginTop: '0.5em',
                            marginBottom: '0.5em',
                        },
                    },
                },
            },
        },
    },
    plugins: [
        require('@tailwindcss/typography'),
    ],
}
