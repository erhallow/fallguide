// Local browser test server. NEVER calls beehiiv, even if real env vars exist.
const http = require('node:http');
const fs = require('node:fs/promises');
const path = require('node:path');
const { createSubscribeHandler } = require('../lib/subscribe.cjs');
const root = path.resolve(__dirname, '..');
const handler = createSubscribeHandler({
  env: { NODE_ENV: 'test', beehiiv_api: 'mock-only', beehiiv_pub_id: 'pub_00000000-0000-0000-0000-000000000000' },
  fetcher: async (_url, options) => {
    const body = JSON.parse(options.body);
    console.log('mock_beehiiv_request', { placement: body.utm_content });
    return body.email === 'fail@example.com'
      ? { ok: false, status: 500 }
      : { ok: true, status: 200, json: async () => ({ data: { id: 'sub_mock', status: body.email === 'pending@example.com' ? 'pending' : 'active' } }) };
  }
});
const files = new Map([
  ['/', ['index.html', 'text/html; charset=utf-8']],
  ['/scripts/subscribe.js', ['scripts/subscribe.js', 'text/javascript']],
  ['/scripts/link-analytics.js', ['scripts/link-analytics.js', 'text/javascript']],
  ['/og.png', ['og.png', 'image/png']]
]);
http.createServer(async (req, res) => {
  const pathname = new URL(req.url, 'http://127.0.0.1:8766').pathname;
  if (pathname === '/api/subscribe') {
    let body = '';
    for await (const chunk of req) {
      body += chunk;
      if (Buffer.byteLength(body) > 2048) {
        res.writeHead(413, { 'Content-Type': 'application/json' });
        return res.end(JSON.stringify({ ok: false, message: 'The request is too large.' }));
      }
    }
    req.body = body;
    res.setHeader('X-Signup-Test-Mode', 'mock');
    res.on('finish', () => console.log('mock_signup_response', { status: res.statusCode }));
    return handler(req, res);
  }
  const file = files.get(pathname);
  if (!file) { res.writeHead(404); return res.end('Not found'); }
  try {
    res.writeHead(200, { 'Content-Type': file[1], 'Cache-Control': 'no-store' });
    res.end(await fs.readFile(path.join(root, file[0])));
  } catch (_) { res.end(); }
}).listen(8766, '127.0.0.1', () => console.log('MOCK ONLY: http://127.0.0.1:8766 — no real subscribers or emails.'));
