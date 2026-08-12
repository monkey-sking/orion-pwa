// Build step: merge ngsl_gloss.json into APP_DATA, inject into index_template.html,
// and emit both index.html (root) and dist/index.html (deployed bundle).
const fs = require('fs');

const tpl = fs.readFileSync('index_template.html', 'utf8');
const dataCode = fs.readFileSync('data.js', 'utf8');
const m = dataCode.match(/^window\.APP_DATA\s*=\s*([\s\S]*);\s*$/);
if (!m) { console.error('!! cannot parse data.js (expected: window.APP_DATA = {...};)'); process.exit(1); }
const data = JSON.parse(m[1]);
data.ngslGloss = JSON.parse(fs.readFileSync('ngsl_gloss.json', 'utf8'));

const inlined = tpl.replace('__APP_DATA__', JSON.stringify(data));
fs.writeFileSync('index.html', inlined);
fs.writeFileSync('dist/index.html', inlined);

console.log('built index.html  bytes:', inlined.length);
console.log('ngslGloss entries:', Object.keys(data.ngslGloss).length);
console.log('has __APP_DATA__ leftover:', inlined.includes('__APP_DATA__'));
console.log('has core tab:', inlined.includes('data-tab="core"'));
console.log('has ngslGloss field:', inlined.includes('"ngslGloss"'));
