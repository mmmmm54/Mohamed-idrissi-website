/*
  Checks the deployed site the way an AI agent sees it. Run after a deploy:
    npm run check:live              (checks https://mohamedidrissi.site)
    npm run check:live -- <url>     (checks another deployment)
  Follows redirects, like `curl -L`, and prints one line per check.
*/
const origin = (process.argv[2] || 'https://mohamedidrissi.site').replace(/\/$/, '');
const results = [];
const check = (name, ok, detail = '') => results.push({ name, ok, detail });

async function get(path, accept) {
  const response = await fetch(origin + path, { headers: accept ? { Accept: accept } : {}, redirect: 'follow' });
  return { status: response.status, type: response.headers.get('content-type') || '', vary: response.headers.get('vary') || '', body: await response.text() };
}
const varyHasAccept = (vary) => vary.split(',').map((part) => part.trim().toLowerCase()).includes('accept');

const markdownHome = await get('/', 'text/markdown');
check('Homepage, Accept: text/markdown → 200', markdownHome.status === 200, String(markdownHome.status));
check('  … Content-Type: text/markdown', markdownHome.type.startsWith('text/markdown'), markdownHome.type);
check('  … Vary: Accept', varyHasAccept(markdownHome.vary), markdownHome.vary || 'none');
check('  … Markdown body, not HTML', markdownHome.body.startsWith('# ') && !/<html/i.test(markdownHome.body), `${markdownHome.body.length} chars`);

const htmlHome = await get('/', 'text/html');
check('Homepage, Accept: text/html → HTML', htmlHome.status === 200 && htmlHome.type.startsWith('text/html') && /<html/i.test(htmlHome.body), htmlHome.type);
check('  … Vary: Accept', varyHasAccept(htmlHome.vary), htmlHome.vary || 'none');

const probe = `/__agent-404-probe-${Date.now().toString(36)}`;
const markdown404 = await get(probe, 'text/markdown');
check('Missing page, Accept: text/markdown → 404', markdown404.status === 404, String(markdown404.status));
check('  … Content-Type: text/markdown', markdown404.type.startsWith('text/markdown'), markdown404.type);
check('  … explains the error and links to sitemap / llms.txt', markdown404.body.length >= 20 && /sitemap\.xml|llms\.txt/.test(markdown404.body), `${markdown404.body.length} chars`);
const html404 = await get(probe, 'text/html');
check('Missing page, Accept: text/html → HTML 404', html404.status === 404 && html404.type.startsWith('text/html'), `${html404.status} ${html404.type}`);

const llms = await get('/llms.txt');
check('/llms.txt has a "## When to use" section', llms.status === 200 && /^## When to use$/m.test(llms.body), String(llms.status));

const homeHtml = htmlHome.body;
const text = homeHtml.replace(/<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>/g, ' ').replace(/<[^>]+>/g, ' ').replace(/&[a-z#0-9]+;/gi, ' ').replace(/\s+/g, ' ').trim();
const ratio = text.length / Buffer.byteLength(homeHtml);
check('Homepage text without JavaScript ≥ 500 chars and ≥ 5%', text.length >= 500 && ratio >= 0.05, `${text.length} chars, ${(ratio * 100).toFixed(1)}%`);

const person = [...homeHtml.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)].map((match) => JSON.parse(match[1])).find((item) => item['@type'] === 'Person');
check('Person JSON-LD has a description', Boolean(person?.description), person?.description?.slice(0, 50) || 'missing');

for (const page of ['/about/', '/contact/', '/privacy/']) {
  const response = await get(page, 'text/html');
  const main = (response.body.match(/<main[\s\S]*?<\/main>/) || [''])[0].replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
  check(`${page} → 200 with ≥ 500 chars`, response.status === 200 && main.length >= 500, `${response.status}, ${main.length} chars`);
}

const insights = await fetch(`${origin}/_vercel/insights/script.js`, { redirect: 'follow' });
check('No analytics loader while Vercel Analytics is off', !homeHtml.includes('_vercel/insights') || insights.ok, `insights ${insights.status}`);

let failed = 0;
for (const { name, ok, detail } of results) {
  if (!ok) failed += 1;
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${name}${detail ? `  (${detail})` : ''}`);
}
console.log(`\n${results.length - failed}/${results.length} checks passed against ${origin}`);
process.exitCode = failed ? 1 : 0;
