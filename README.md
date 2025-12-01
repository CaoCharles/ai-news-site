# AI News / AI Trends Website

An Astro-based static site for tracking AI ecosystem trends and technical documentation.

## Tech Stack
- **Framework**: Astro
- **Styling**: Tailwind CSS
- **Content**: Markdown/MDX with Astro Content Collections

## Project Structure
```
/
  src/
    layouts/    # BaseLayout, ArticleLayout
    pages/      # index, world, technology, podcasts, [slug]
    components/ # UI components
    content/    # Content collections config
      posts/    # Markdown articles
  public/       # Static assets
```

## Setup & Development

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Start Dev Server**
   ```bash
   npm run dev
   ```

3. **Build for Production**
   ```bash
   npm run build
   ```

## Deployment (GitHub Pages)

This project is configured to deploy to GitHub Pages via GitHub Actions.

1. Go to your repository **Settings** > **Pages**.
2. Under "Build and deployment", select **GitHub Actions** as the source.
3. The workflow defined in `.github/workflows/deploy.yml` will automatically build and deploy on push to `main`.

> **IMPORTANT**: Update `astro.config.mjs` with your actual repository name in the `base` property (currently set to `/ai-trends-site`).

## Contribution Guide for Agents

### Adding New Content
1. Create a new Markdown file in `src/content/posts/`.
2. Use the following frontmatter schema:
   ```yaml
   ---
   title: "Article Title"
   date: "YYYY-MM-DD"
   category: "Technology" # Options: World, Business, Technology, Health, Sports, Culture, Podcast
   source: "Google" # Options: Google, OpenAI, Anthropic, Mixed
   tags: ["Tag1", "Tag2"]
   summary: "Short summary..."
   heroImage: "/images/placeholders/image.jpg"
   readingTime: "5 Minutes"
   ---
   ```
3. Name your branch `feature/<topic>-news-YYYYMMDD`.

### Tools
- Use `codex-cli` for component refactoring.
- Use `gemini-cli` for architectural decisions.
