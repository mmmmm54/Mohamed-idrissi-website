/*
  Brand identity projects, one page each under /branding/<slug>/.
  The homepage "Made to stand out" tab and the "next brand" link at the
  bottom of every brand page read this list, so order here is order there.

  palette: CSS custom property names from global.css, shown as dots.
  Facts only: lines below come from the supplied brand material.
*/
export interface Brand {
  slug: string;
  name: string;
  kind: string;
  line: string;
  mark: { src: string; width: number; height: number };
  cover: { src: string; alt: string };
  palette: string[];
}

export const brands: Brand[] = [
  {
    slug: 'learnx',
    name: 'LearnX',
    kind: 'Brand identity',
    line: 'One mark, three ideas: brilliance, technology and programming.',
    mark: { src: '/branding/learnx/mark.webp', width: 660, height: 200 },
    cover: { src: '/branding/learnx/hero.webp', alt: 'White LearnX logo on a deep blue wave background' },
    palette: ['--learnx-navy', '--learnx-teal', '--learnx-aqua', '--learnx-mist'],
  },
  {
    slug: 'vanysis',
    name: 'Vanysis',
    kind: 'Brand identity',
    line: 'A skin performance brand in glass, light and precision.',
    mark: { src: '/branding/vanysis/wordmark.webp', width: 789, height: 226 },
    cover: { src: '/branding/vanysis/product-system.webp', alt: 'Vanysis device and serum side by side' },
    palette: ['--vanysis-ink', '--vanysis-ocean', '--vanysis-sage', '--vanysis-aqua'],
  },
  {
    slug: 'exploremorocco',
    name: 'ExploreMorocco',
    kind: 'Art direction',
    line: 'Northern Morocco as a travel journal in nine frames.',
    mark: { src: '/images/clients/exploremorocco.png', width: 350, height: 100 },
    cover: { src: '/projects/exploremorocco/selected/web/explore-morocco_02%201.png.webp', alt: 'ExploreMorocco poster: a white street seen through a teal arch' },
    palette: ['--explore-teal', '--explore-sea', '--explore-foam', '--explore-sand'],
  },
];

export const brandIndex = (slug: string) => brands.findIndex((brand) => brand.slug === slug);
export const nextBrand = (slug: string) => brands[(brandIndex(slug) + 1) % brands.length];
export const brandNumber = (slug: string) => String(brandIndex(slug) + 1).padStart(2, '0');
