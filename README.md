# Mohamed’s portfolio

## Add project images

Each project has a folder in `public/projects/`: `mat`, `justfit`, `exploremorocco`, `maalem`, `aqluma`, and `vanysis`.

- Replace `cover.jpg` to change the homepage and case-study cover.
- Add gallery images named `01.jpg`, `02.jpg`, `03.jpg`, etc. PNG and WebP also work. They appear automatically, in filename order, after rebuilding.
- Add `cover.mp4` to MAALEM’s folder for its homepage background video.

Use compressed images and keep important subjects near the centre, as cover crops vary by screen size.

## Edit case studies

Edit the matching Markdown file in `src/content/projects/`. The fields control the title, description, order, services, challenge, approach, deliverables and results. No layout edits are needed.

The narratives are drafts, not verified records of client work. Before publishing, confirm the scope and dates, replace illustrative imagery, and add genuine outcomes or client feedback. Search for `TODO` to find missing material. The shared draft notice and outcomes reminder live in `src/pages/work/[slug].astro`; remove them only after every project has been verified.

## Preview and build

Run `npm run dev` for the local preview and `npm run build` to check and build the site. No additional packages are needed for the current implementation.

Shared visual settings are in `src/styles/global.css`; case-study styles are in `src/styles/case.css`.
