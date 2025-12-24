# AGENTS.md - Programming Assistant Guidelines

## Project Overview

This repository contains the "LLMs for Backend Engineers" book, a Docusaurus-based documentation project that explains large language models from an engineering perspective. The book targets backend engineers who want to understand LLMs without academic overload or hype-driven narratives.

## Project Structure

- `/documentation` - Main Docusaurus project directory
  - `/docs` - Contains book chapters and content
    - `/chapters` - Main book chapters
    - `/advanced_transformer` - Deep dive into Transformer architecture
  - `/src` - Custom Docusaurus components and styling
  - `/static` - Static assets and resources
  - `/blog` - Blog posts (if any)
  - `/draft` - Draft content
  - `docusaurus.config.ts` - Main site configuration
  - `sidebars.ts` - Navigation sidebar configuration

## Technology Stack

- **Framework**: Docusaurus v3.9.2
- **Language**: TypeScript (for configuration and custom components)
- **Content Format**: Markdown/MDX
- **Package Manager**: npm
- **Deployment**: GitHub Pages

## Development Guidelines

### Content Creation
- Follow the existing writing style and format (see existing chapters for examples)
- Use proper frontmatter in Markdown files: `sidebar_label`, `sidebar_position`
- Add appropriate metadata to `sidebars.ts` when creating new content
- Ensure content is aimed at backend engineers with practical, engineering-focused explanations
- Avoid academic jargon, heavy mathematical derivations, and hype-driven narratives

### Code Standards
- TypeScript configuration follows Docusaurus recommended settings
- React components used for custom functionality
- Consistent naming conventions for files and components
- Follow Docusaurus theme and styling principles

### Development Workflow
- Use `./start_docs.sh` or `npm run start` for local development
- Test changes locally before committing
- Follow the existing directory structure for new content
- Update `sidebars.ts` to include new pages in navigation

## Common Tasks

### Adding New Chapters
1. Create new Markdown file in `/documentation/docs/chapters/`
2. Add proper frontmatter with `sidebar_label` and `sidebar_position`
3. Include the new file in `sidebars.ts` navigation
4. Use existing chapters as format reference

### Custom Components
- Place custom React components in `/documentation/src/`
- Follow Docusaurus component integration guidelines
- Test component rendering in development environment

### Styling Changes
- Use existing CSS classes and Docusaurus theme where possible
- Add custom CSS in `/documentation/src/css/` if needed
- Test responsive design on different screen sizes

## Testing and Verification

- Use `npm run build` to verify that changes build successfully
- Test locally with `npm run serve` to preview build output
- Ensure all links and navigation work correctly
- Verify that MDX components render properly

## Deployment

- Use `npm run build` followed by `npm run deploy` for GitHub Pages deployment
- For this project: `GIT_USER=kingson4wu npm run deploy`
- Verify deployment at `https://kingson4wu.github.io/LLMs-for-Backend-Engineers/`

## Special Considerations

- This is a work-in-progress project with content that may be revised
- The book targets backend engineers specifically
- Content should focus on understanding how LLMs work from an engineering perspective
- Emphasis is on practical understanding rather than theoretical concepts
- The goal is clarity and reasoning, not evangelism
- Important note: Book content has not been manually proofread and may contain errors