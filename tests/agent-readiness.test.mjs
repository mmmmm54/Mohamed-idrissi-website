/*
  Agent-readiness checks on the built site. Run after a build:
    npm run build && npm test
  Uses only Node's built-in test runner; reads dist/ and vercel.json.
*/
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { packQueue, unpackQueue } from '../src/scripts/poster-queue.ts';

const root = path.resolve(import.meta.dirname, '..');
const dist = path.join(root, 'dist');
const read = (file) => fs.readFileSync(path.join(dist, file), 'utf8');
const exists = (file) => fs.existsSync(path.join(dist, file)) && fs.statSync(path.join(dist, file)).isFile();

/* Visible text of an HTML page: no scripts, styles or tags. */
const visibleText = (html) =>
  html
    .replace(/<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>/g, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&[a-z#0-9]+;/gi, ' ')
    .replace(/\s+/g, ' ')
    .trim();
const mainText = (html) => visibleText((html.match(/<main[\s\S]*?<\/main>/) || [html])[0]);
const jsonLd = (html) =>
  [...html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)].map((match) => JSON.parse(match[1]));

/* ---------- Vercel routing, evaluated in the documented order ---------- */
const vercel = JSON.parse(fs.readFileSync(path.join(root, 'vercel.json'), 'utf8'));
function resolveRequest(pathname, accept) {
  const headers = {};
  const matches = (route) => {
    if (!new RegExp(route.src).test(pathname)) return false;
    return (route.has || []).every((rule) => {
      assert.equal(rule.type, 'header');
      const value = rule.key.toLowerCase() === 'accept' ? accept : undefined;
      return value !== undefined && new RegExp(`^${rule.value}$`).test(value);
    });
  };
  const fileFor = (p) => {
    const clean = p.replace(/^\//, '');
    if (clean && exists(clean)) return clean;
    const index = path.posix.join(clean, 'index.html');
    return exists(index) ? index : null;
  };
  let phase = 'before';
  for (const route of vercel.routes) {
    if (route.handle === 'filesystem') {
      phase = 'after';
      const file = fileFor(pathname);
      if (file) return { status: 200, file, headers };
      continue;
    }
    if (!matches(route)) continue;
    Object.assign(headers, route.headers || {});
    if (route.continue) continue;
    return { status: route.status || 200, file: route.dest.replace(/^\//, ''), headers, phase };
  }
  return { status: 404, file: '404.html', headers };
}

test('Accept: text/markdown on the homepage returns the Markdown file with Vary: Accept', () => {
  for (const accept of ['text/markdown', 'text/markdown, text/html;q=0.9', 'text/plain, text/markdown']) {
    const result = resolveRequest('/', accept);
    assert.equal(result.status, 200);
    assert.equal(result.file, 'index.md');
    assert.match(result.headers['Content-Type'], /^text\/markdown/);
    assert.equal(result.headers.Vary, 'Accept');
  }
});

test('Browsers still get the HTML homepage, also with Vary: Accept', () => {
  for (const accept of ['text/html,application/xhtml+xml,*/*;q=0.8', '*/*']) {
    const result = resolveRequest('/', accept);
    assert.equal(result.status, 200);
    assert.equal(result.file, 'index.html');
    assert.equal(result.headers.Vary, 'Accept');
  }
});

test('Missing pages return 404 in Markdown for agents and in HTML for browsers', () => {
  const agent = resolveRequest('/__missing-page-probe', 'text/markdown');
  assert.equal(agent.status, 404);
  assert.equal(agent.file, '404.md');
  assert.match(agent.headers['Content-Type'], /^text\/markdown/);
  const browser = resolveRequest('/__missing-page-probe', 'text/html');
  assert.equal(browser.status, 404);
  assert.equal(browser.file, '404.html');
});

test('Existing pages keep serving HTML even when Markdown is asked for', () => {
  for (const page of ['/about/', '/contact/', '/privacy/', '/work/mat/']) {
    const result = resolveRequest(page, 'text/markdown');
    assert.equal(result.status, 200, page);
    assert.match(result.file, /index\.html$/, page);
  }
});

/* ---------- Markdown bodies ---------- */
test('Homepage Markdown is substantial and matches the HTML homepage', () => {
  const md = read('index.md');
  const html = read('index.html');
  assert.match(md, /^# Mohamed Idrissi/);
  assert.ok(md.length > 1500, `index.md is only ${md.length} characters`);
  assert.doesNotMatch(md, /<[a-z][^>]*>/i, 'index.md should not contain HTML');
  for (const slug of fs.readdirSync(path.join(dist, 'work'))) {
    assert.ok(md.includes(`/work/${slug}/`), `index.md is missing project ${slug}`);
  }
  const about = 'I design brand identities, social campaigns and videos, from the first idea to the final files.';
  assert.ok(md.includes(about) && html.includes(about), 'About text differs between Markdown and HTML');
});

test('Markdown 404 explains the error and links to the sitemap and llms.txt', () => {
  const md = read('404.md');
  assert.ok(md.replace(/\s+/g, ' ').length >= 20);
  assert.match(md, /404/);
  assert.match(md, /\(https:\/\/www\.mohamedidrissi\.site\/sitemap\.xml\)/);
  assert.match(md, /\(https:\/\/www\.mohamedidrissi\.site\/llms\.txt\)/);
});

/* ---------- llms.txt (llmstxt.org format) ---------- */
test('llms.txt follows the llmstxt.org structure and has a When to use section', () => {
  const text = read('llms.txt');
  const lines = text.split('\n');
  assert.match(lines[0], /^# \S/, 'first line must be the H1');
  assert.ok(lines.slice(1).some((line) => line.startsWith('> ')), 'needs a blockquote summary');
  assert.equal((text.match(/^# /gm) || []).length, 1, 'exactly one H1');
  assert.doesNotMatch(text, /^#{3,} /m, 'no H3 or deeper headings');
  const sections = text.split(/^## /m).slice(1);
  assert.ok(sections.length >= 3);
  for (const section of sections) {
    const [title, ...rest] = section.split('\n');
    const items = rest.filter((line) => line.trim());
    assert.ok(items.length > 0, `section ${title} is empty`);
    for (const item of items) assert.match(item, /^- \[[^\]]+\]\([^)]+\)(: .+)?$/, `section "${title}" has a non-link line: ${item}`);
  }
  const whenToUse = sections.find((section) => section.startsWith('When to use'));
  assert.ok(whenToUse, 'missing ## When to use');
  assert.ok(whenToUse.split('\n').filter((line) => line.startsWith('- [')).length >= 4);
});

/* ---------- Homepage HTML without JavaScript ---------- */
test('Homepage ships meaningful text in raw HTML, above a 5% content ratio', () => {
  const html = read('index.html');
  const text = visibleText(html);
  const ratio = text.length / Buffer.byteLength(html);
  assert.ok(text.length >= 500, `only ${text.length} characters of text`);
  assert.ok(ratio >= 0.05, `content ratio ${(ratio * 100).toFixed(1)}%`);
});

test('Every page has one H1 and heading levels never skip', () => {
  const pages = ['index.html', 'about/index.html', 'contact/index.html', 'privacy/index.html', '404.html',
    ...fs.readdirSync(path.join(dist, 'work')).map((slug) => `work/${slug}/index.html`)];
  for (const page of pages) {
    const levels = [...read(page).matchAll(/<h([1-6])\b/g)].map((match) => Number(match[1]));
    assert.equal(levels.filter((level) => level === 1).length, 1, `${page}: one h1`);
    levels.reduce((previous, level) => {
      assert.ok(level <= previous + 1, `${page}: h${previous} jumps to h${level}`);
      return level;
    }, 1);
  }
});

test('Homepage poster cards ship two images and a compact queue for the rest', () => {
  const html = read('index.html');
  const stacks = [...html.matchAll(/<div class="cover-stack"([^>]*)>([\s\S]*?)<\/div>/g)];
  assert.ok(stacks.length >= 10);
  for (const [, attributes, inner] of stacks) {
    const count = Number(attributes.match(/data-count="(\d+)"/)[1]);
    const base = attributes.match(/data-base="([^"]+)"/)[1];
    const queue = unpackQueue(attributes.match(/data-queue="([^"]*)"/)?.[1], base);
    const images = [...inner.matchAll(/<img\b[^>]*src="([^"]+)"/g)].map((match) => match[1]);
    assert.ok(images.length <= 2);
    assert.equal(images.length + queue.length, count, `${base}: posters lost`);
    for (const url of [...images, ...queue]) assert.ok(exists(decodeURIComponent(url).replace(/^\//, '')), `missing ${url}`);
  }
});

test('Poster queue packs and unpacks without losing or reordering posters', () => {
  const base = '/projects/demo/selected/web/';
  const urls = [`${base}a.jpg.webp`, `${base}New%20folder/b.jpg.webp`, `${base}c%20%E2%80%94%20d.png.webp`];
  assert.deepEqual(unpackQueue(packQueue(urls, base), base), urls);
  assert.deepEqual(unpackQueue('', base), []);
  assert.deepEqual(unpackQueue(undefined, base), []);
  assert.throws(() => packQueue(['/elsewhere/a.webp'], base));
  assert.throws(() => packQueue([`${base}a|b.webp`], base));
});

/* ---------- Structured data and trust pages ---------- */
test('Person JSON-LD has a description on every page', () => {
  for (const page of ['index.html', 'about/index.html', 'work/mat/index.html']) {
    const person = jsonLd(read(page)).find((item) => item['@type'] === 'Person');
    assert.ok(person, `${page}: no Person`);
    assert.ok(person.description && person.description.length > 50, `${page}: Person without description`);
  }
});

test('About, Contact and Privacy pages exist with real content and are listed in the sitemap', () => {
  const sitemap = read('sitemap.xml');
  for (const page of ['about', 'contact', 'privacy']) {
    const html = read(`${page}/index.html`);
    assert.ok(mainText(html).length >= 500, `${page}: only ${mainText(html).length} characters`);
    assert.match(html, new RegExp(`<link rel="canonical" href="https://www\\.mohamedidrissi\\.site/${page}/">`));
    assert.ok(sitemap.includes(`https://www.mohamedidrissi.site/${page}/`), `${page} missing from sitemap`);
    assert.ok(read('index.html').includes(`href="/${page}/"`), `homepage does not link to ${page}`);
  }
  assert.match(read('contact/index.html'), /mailto:mohamedidrissi205@gmail\.com/);
  assert.match(read('contact/index.html'), /https:\/\/wa\.me\/212691865970/);
});

test('Analytics loader stays off until Vercel Analytics is enabled, and Privacy says so', () => {
  const html = read('index.html');
  assert.doesNotMatch(html, /_vercel\/insights/, 'analytics script would 404 until enabled on Vercel');
  assert.match(read('privacy/index.html'), /No analytics or tracking/);
});
