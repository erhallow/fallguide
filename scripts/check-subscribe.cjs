const assert = require('node:assert/strict');
const { test } = require('node:test');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const { createSubscribeHandler } = require('../lib/subscribe.cjs');
const ENV = { beehiiv_api: 'fake-test-key', beehiiv_pub_id: 'pub_00000000-0000-0000-0000-000000000000', NODE_ENV: 'production' };
const valid = { email: ' reader@example.com ', placement: 'top', website: '' };

function setup({ env = ENV, status = 200, data = { id: 'sub_test', status: 'active' }, error, jsonError, now } = {}) {
  const calls = [], logs = [];
  const handler = createSubscribeHandler({ env, now, logger: { error: (...x) => logs.push(x) }, fetcher: async (url, options) => {
    calls.push({ url, options });
    if (error) throw error;
    return { ok: status >= 200 && status < 300, status, json: async () => {
      if (jsonError) throw new Error('upstream private data');
      return { data };
    } };
  } });
  return { calls, logs, async request(body = valid, extras = {}) {
    const req = { method: 'POST', headers: { origin: 'https://fallguide.nwiexplored.com', 'content-type': 'application/json' }, socket: { remoteAddress: '127.0.0.1' }, body, ...extras };
    const res = { headers: {}, setHeader(name, value) { this.headers[name] = value; }, end(value) { this.body = JSON.parse(value); } };
    await handler(req, res);
    return res;
  } };
}

test('creates the correct free newsletter subscription using only server-held configuration', async () => {
  const api = setup();
  const res = await api.request();
  assert.equal(res.statusCode, 200);
  assert.equal(res.body.ok, true);
  assert.equal(res.headers['Cache-Control'], 'no-store');
  assert.equal(api.calls[0].url, `https://api.beehiiv.com/v2/publications/${ENV.beehiiv_pub_id}/subscriptions`);
  assert.equal(api.calls[0].options.headers.Authorization, 'Bearer fake-test-key');
  assert.deepEqual(JSON.parse(api.calls[0].options.body), {
    email: 'reader@example.com', reactivate_existing: false, send_welcome_email: true,
    double_opt_override: 'not_set', utm_source: 'fall_guide', utm_medium: 'website',
    utm_campaign: 'fall_guide_2026', utm_content: 'newsletter_top', referring_site: 'https://fallguide.nwiexplored.com/'
  });
  assert.equal(api.calls[0].options.redirect, 'error');
  assert.ok(api.calls[0].options.signal instanceof AbortSignal);
  assert.equal(JSON.stringify(res.body).includes('reader@'), false);
  assert.equal(JSON.stringify(res.body).includes('fake-test-key'), false);
});

test('bottom form attribution cannot override credentials, destination or consent settings', async () => {
  const api = setup();
  await api.request({ ...valid, placement: 'bottom', apiKey: 'attacker', publicationId: 'wrong', reactivate_existing: true, double_opt_override: 'off' });
  const sent = JSON.parse(api.calls[0].options.body);
  assert.equal(sent.utm_content, 'newsletter_bottom');
  assert.equal(sent.reactivate_existing, false);
  assert.equal(sent.double_opt_override, 'not_set');
  assert.equal(api.calls[0].options.headers.Authorization, 'Bearer fake-test-key');
});

test('accepted active, validating and pending responses do not falsely promise confirmation', async () => {
  for (const status of ['active', 'validating', 'pending']) {
    const res = await setup({ data: { id: 'sub_test', status } }).request();
    assert.equal(res.statusCode, 200);
    assert.match(res.body.message, /confirmation steps/);
  }
});

test('unsubscribed, invalid, paused, unknown and malformed results are not called successful', async () => {
  for (const status of ['inactive', 'invalid', 'paused', 'unknown', undefined]) {
    const res = await setup({ data: { id: 'sub_test', status } }).request();
    assert.equal(res.body.ok, false);
    assert.equal(res.statusCode, 409);
  }
  assert.equal((await setup({ data: {} }).request()).body.ok, false);
});

test('missing or malformed server configuration fails safely before contacting beehiiv', async () => {
  for (const env of [{}, { beehiiv_api: 'secret' }, { ...ENV, beehiiv_pub_id: 'https://evil.test' }]) {
    const api = setup({ env });
    assert.equal((await api.request()).statusCode, 503);
    assert.equal(api.calls.length, 0);
    assert.equal(JSON.stringify(api.logs).includes('secret'), false);
  }
});

test('rejects unsafe methods, origins, content types, malformed JSON and oversized input', async () => {
  for (const [extras, body, status] of [
    [{ method: 'GET' }, valid, 405],
    [{ headers: { origin: 'https://evil.test', 'content-type': 'application/json' } }, valid, 403],
    [{ headers: { 'content-type': 'application/json' } }, valid, 403],
    [{ headers: { origin: 'null', 'content-type': 'application/json' } }, valid, 403],
    [{ headers: { origin: 'https://fallguide.nwiexplored.com', 'content-type': 'text/plain' } }, valid, 415],
    [{}, '{', 400], [{}, null, 400], [{}, [], 400], [{}, 'x'.repeat(2050), 413],
    [{}, { ...valid, extra: 'x'.repeat(2050) }, 413]
  ]) {
    const api = setup();
    assert.equal((await api.request(body, extras)).statusCode, status);
    assert.equal(api.calls.length, 0);
  }
});

test('validates email, placement and honeypot server-side', async () => {
  for (const body of [{ ...valid, email: 'no-email' }, { ...valid, email: 'a\nb@example.com' }, { ...valid, email: 'a'.repeat(255)+'@example.com' }, { ...valid, email: {} }, { ...valid, placement: 'evil' }, { ...valid, website: 'bot' }, { ...valid, website: undefined }]) {
    const api = setup();
    assert.equal((await api.request(body)).statusCode, 400);
    assert.equal(api.calls.length, 0);
  }
});

test('handles parsed JSON, raw JSON and Buffer bodies', async () => {
  for (const body of [valid, JSON.stringify(valid), Buffer.from(JSON.stringify(valid))]) {
    assert.equal((await setup().request(body)).statusCode, 200);
  }
});

test('throttles bursts per instance and expires old rate-limit buckets', async () => {
  let time = 1000;
  const api = setup({ now: () => time });
  for (let i = 0; i < 5; i++) assert.equal((await api.request()).statusCode, 200);
  const limited = await api.request();
  assert.equal(limited.statusCode, 429);
  assert.equal(limited.headers['Retry-After'], '600');
  assert.equal(api.calls.length, 5);
  time += 600001;
  assert.equal((await api.request()).statusCode, 200);
});

test('upstream failures, bad JSON and network errors stay sanitized', async () => {
  for (const settings of [{ status: 400 }, { status: 401 }, { status: 500 }, { jsonError: true }, { error: new Error('private fake-test-key reader@example.com') }]) {
    const api = setup(settings);
    const res = await api.request();
    assert.equal(res.statusCode, 502);
    assert.equal(JSON.stringify([res.body, api.logs]).includes('fake-test-key'), false);
    assert.equal(JSON.stringify([res.body, api.logs]).includes('reader@example.com'), false);
  }
  assert.equal((await setup({ status: 429 }).request()).statusCode, 429);
});

const clientSource = fs.readFileSync(path.join(__dirname, 'subscribe.js'), 'utf8');
function client({ protocol = 'https:', response = { ok: true, message: 'Signup received.' }, httpOk = true, error, validEmail = true } = {}) {
  const sent = [], analytics = [], handlers = {};
  let resolveRequest;
  const pending = new Promise(resolve => { resolveRequest = resolve; });
  const input = { value: ' reader@example.com ', disabled: false, attributes: {}, checkValidity: () => validEmail,
    setAttribute(name, value) { this.attributes[name] = value; },
    removeAttribute(name) { delete this.attributes[name]; },
    focus() { this.focused = true; } };
  const button = { textContent: 'Subscribe for free', disabled: true };
  const classes = new Set();
  const status = { textContent: '', classList: { add: x => classes.add(x), remove: x => classes.delete(x) } };
  const form = {
    dataset: { subscribeForm: 'top' },
    querySelector: selector => selector === '[name="email"]' ? input : selector.startsWith('button') ? button : selector === '[role="status"]' ? status : { value: '' },
    addEventListener: (type, handler) => { handlers[type] = handler; },
    setAttribute() {}, removeAttribute() {}
  };
  const context = vm.createContext({
    document: { querySelectorAll: () => [form] }, location: { protocol, hostname: 'fallguide.nwiexplored.com' },
    window: { va: (...args) => analytics.push(args) }, AbortController, setTimeout, clearTimeout, SyntaxError, TypeError,
    fetch: async (url, options) => {
      sent.push({ url, options });
      await pending;
      if (error) throw error;
      return { ok: httpOk, json: async () => response };
    }
  });
  vm.runInContext(clientSource, context);
  return { input, button, status, classes, sent, analytics, resolveRequest,
    submit: () => handlers.submit?.({ preventDefault() {} }) };
}

test('client sends email by POST, blocks double submit and clears it only on success', async () => {
  const page = client();
  const first = page.submit();
  await page.submit();
  assert.equal(page.sent.length, 1);
  assert.equal(page.button.disabled, true);
  assert.equal(page.sent[0].url, '/api/subscribe');
  assert.deepEqual(JSON.parse(page.sent[0].options.body), { email: 'reader@example.com', placement: 'top', website: '' });
  page.resolveRequest();
  await first;
  assert.equal(page.input.value, '');
  assert.equal(page.input.disabled, true);
  assert.equal(page.button.textContent, 'Signup received');
  assert.equal(JSON.stringify(page.analytics).includes('reader@'), false);
});

test('client failure preserves email and re-enables retry without firing signup analytics', async () => {
  const page = client({ httpOk: false, response: { ok: false, message: 'Try later.' } });
  page.resolveRequest();
  await page.submit();
  assert.equal(page.input.value, ' reader@example.com ');
  assert.equal(page.button.disabled, false);
  assert.equal(page.status.textContent, 'Try later.');
  assert.equal(page.classes.has('is-error'), true);
  assert.equal(page.analytics.length, 0);
});

test('client network failure offers retry without a removed link or raw error disclosure', async () => {
  const page = client({ error: new TypeError('private network details') });
  page.resolveRequest();
  await page.submit();
  assert.match(page.status.textContent, /try again shortly/);
  assert.equal(page.status.textContent.includes('link below'), false);
  assert.equal(page.status.textContent.includes('private'), false);
  assert.equal(page.button.disabled, false);
});

test('local file preview stays clean and cannot submit to production', async () => {
  const page = client({ protocol: 'file:' });
  await page.submit();
  assert.equal(page.sent.length, 0);
  assert.equal(page.button.disabled, true);
  assert.equal(page.status.textContent, '');
});

test('invalid email shows a compact inline error only after submission', async () => {
  const page = client({ validEmail: false });
  assert.equal(page.status.textContent, '');
  await page.submit();
  assert.equal(page.sent.length, 0);
  assert.equal(page.status.textContent, 'Enter a valid email address.');
  assert.equal(page.input.attributes['aria-invalid'], 'true');
  assert.equal(page.input.focused, true);
  assert.equal(page.button.disabled, false);
});
