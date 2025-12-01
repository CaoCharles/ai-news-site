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

This project is configured to deploy automatically to GitHub Pages using GitHub Actions.

### Setup
1. Go to your repository on GitHub.
2. Navigate to **Settings** > **Pages**.
3. Under **Build and deployment**, set **Source** to **GitHub Actions**.

### Usage
Simply push your changes to the `main` branch. The workflow defined in `.github/workflows/deploy.yml` will automatically build and deploy your site.

> **Note**: `astro.config.mjs` has been configured with `base: '/multi_agent'` to match your repository name.

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
