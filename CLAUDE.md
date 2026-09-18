# CLAUDE.md — Mohamed Idrissi portfolio

Working rules for this repository. Read before changing anything.

## Stack

- **Astro + vanilla CSS only.** No React, no Tailwind, no CSS framework, no UI kit.
- **No new packages without asking.** Current dependencies: `astro`, `@astrojs/check`, `typescript`. If something seems to need a package, propose it first and wait.
- Content lives in `src/content/projects/*.md` and is typed by `src/content/config.ts`.
- Pages are `.astro` files under `src/pages/`. Shared shell is `src/layouts/BaseLayout.astro`.

## Design tokens

- **Every color, font and spacing value goes in a CSS variable** in `src/styles/global.css` under `:root`. No raw hex, no raw `px`/`rem` magic numbers scattered through rules. Per-project brand colors are defined as tokens and mapped onto cards with `data-project="<slug>"`.
- Type scale uses `clamp()` so it tunes itself. Keep it that way.

## Visual identity

- **Playful, confident, editorial.** Big type, strong color blocks, generous whitespace, a little motion.
- **Typography:** `Bricolage Grotesque` for display and body, `Space Mono` for UI, labels and metric lines. No other families.
- **Accent:** electric blue `--blue: #2a37dd`. It is the accent, not the background.
- Each project card carries its own brand background color. Text color adapts per card for contrast.

## Content rules

- **No Instagram link anywhere.** Behance, WhatsApp and email only.
- **No content taken from the reference site.** `reference/` holds a screenshot used for layout feel only. Never copy its words, names, projects or claims.
- **Never invent metrics, clients or verifiable claims.** No performance numbers, no client names, no awards unless Mohamed supplied them.
- Draft narrative copy written in his absence is allowed when he asks for it, but the file must carry a `DRAFT COPY` comment under the frontmatter and the year and scope lines must be confirmed before launch.
- Anything genuinely unknown is written as a visible `TODO` and listed back to him.
- Case study copy is first person, short, confident, no buzzwords.

## Assets

- One cover per project: `public/projects/<slug>/cover.jpg`. Swap the file, nothing else changes.
- Case study gallery images: `public/projects/<slug>/01.jpg`, `02.jpg`, … They are picked up automatically in numeric order, so adding an image is a file drop.
- Optional looping video: `public/projects/<slug>/cover.mp4`. If it exists it replaces the cover image on that project's homepage card.
- Project slug = markdown filename = folder name in `public/projects/`.
- `assets-source/` keeps the untouched originals (PNG / WebP). It is never served or built.

## Types

- Node built-ins used at build time (`node:fs`, `node:path`) are typed by hand in `src/env.d.ts` so the project does not need `@types/node`. Extend that file rather than installing types.

## Commands

```
npm run dev      # local dev server
npm run build    # astro check + build
```
