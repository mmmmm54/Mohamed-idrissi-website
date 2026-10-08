/*
  One source of truth for facts about Mohamed that appear in more than one place:
  the Markdown homepage, llms.txt, the About / Contact / Privacy pages and the
  structured data. Facts only: nothing here is a claim Mohamed has not supplied.
*/

export const SITE_URL = 'https://www.mohamedidrissi.site';

export const person = {
  name: 'Mohamed Idrissi',
  role: 'Graphic designer & creative director',
  city: 'Tétouan',
  country: 'Morocco',
  experienceYears: 4,
  email: 'mohamedidrissi205@gmail.com',
  whatsapp: '+212691865970',
  whatsappDisplay: '+212 691 865 970',
  whatsappUrl: 'https://wa.me/212691865970',
  behanceUrl: 'https://www.behance.net/Mohamed_Idrissi',
};

/* One sentence, reused as the Person description in JSON-LD and the llms.txt summary. */
export const shortBio =
  'Graphic designer and creative director in Tétouan, Morocco, with 4 years of experience in sports, fitness and lifestyle branding: brand identity, social media campaigns and video.';

/* Same wording as the About section on the homepage. */
export const aboutParagraphs = [
  'I’m a graphic designer and creative director from Tétouan, with 4 years of experience in sports, fitness and lifestyle branding. I design brand identities, social campaigns and videos, from the first idea to the final files.',
  'Today I pair brand strategy with AI-assisted production to deliver identities, campaigns and films faster, without losing the craft.',
];

/* Same three services as “What I do” on the homepage. */
export const services = [
  { title: 'Brand identity', text: 'Strategy, logos, typography, colour and guidelines.' },
  { title: 'Art direction', text: 'Campaign concepts, editorial direction and social media systems.' },
  { title: 'Creative production', text: 'AI-assisted imagery, cinematic films and video editing.' },
];

export const process = ['Find the idea', 'Explore the direction', 'Make it work'];

/* Brands Mohamed has worked with. Supplied logos live in public/images/clients/; sizing is handled in CSS. */
export const collaborators = [
  { name: 'ExploreMorocco', file: 'exploremorocco.png', style: 'wide' },
  { name: 'MAALEM', file: 'maalem.jpg', style: 'maalem' },
  { name: 'Asia This Way', file: 'asia-this-way.png', style: 'compact' },
  { name: 'Moghreb Atletico Tétouan', file: 'mat.png', style: 'crest' },
  { name: 'JustFit', file: 'justfit.png', style: 'standard' },
  { name: 'IS Nutrition', file: 'is-nutrition.png', style: 'nutrition' },
  { name: 'Morocco Travel', file: 'morocco-travel.png', style: 'standard' },
  { name: 'Vanysis', file: 'vanysis.png', style: 'wide' },
  { name: 'Overt', file: 'overt.avif', style: 'wide' },
  { name: 'Nomad Vélo', file: 'nomad-velo.webp', style: 'wide' },
  { name: 'E-Botola', file: 'e-botola.png', style: 'crest' },
  { name: 'Sarasota Paradise', file: 'sarasota-paradise.png', style: 'paradise' },
  { name: 'The Norvale Club', file: 'norvale.png', style: 'norvale' },
  { name: 'Dr. Majed Mikhail', file: 'dr-majed-mikhail.svg', style: 'doctor' },
  { name: 'Bio Care & Beauty', file: 'bio-care-beauty.png', style: 'standard' },
];

/*
  Vercel Web Analytics. Leave false until Analytics is switched on in the Vercel
  dashboard: the script at /_vercel/insights/script.js only exists once it is,
  and loading it earlier logs a 404 for every visitor. The privacy page reads this
  flag too, so it always describes what the site actually does.
*/
export const ANALYTICS_ENABLED = false;
