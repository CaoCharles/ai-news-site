import { getCollection } from 'astro:content';

export async function GET({ }) {
    const posts = await getCollection('posts');
    const searchList = posts.map(post => ({
        title: post.data.title,
        description: post.data.description,
        slug: post.slug,
        category: post.data.category,
        date: post.data.date
    }));

    return new Response(JSON.stringify(searchList), {
        headers: {
            'content-type': 'application/json'
        }
    });
}
