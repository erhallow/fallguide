'use strict';

const { createHash } = require('node:crypto');
const SITE = 'https://fallguide.nwiexplored.com';
const WINDOW_MS = 10 * 60 * 1000;
const MAX_BODY = 2048;
const MESSAGES = {
  unavailable: 'Signup is temporarily unavailable. Please try again shortly.',
  invalid: 'Please enter a valid email address.',
  retry: 'We couldn’t complete your signup. Please try again shortly.',
  limited: 'Too many attempts. Please wait a few minutes before trying again.',
  received: 'Thanks! Your signup was received. Check your inbox for any confirmation steps.'
};

function createSubscribeHandler({ env = process.env, fetcher = globalThis.fetch, now = Date.now, logger = console } = {}) {
  // Best-effort burst protection per warm instance, not a distributed rate limit.
  // Use a Vercel Firewall rate-limit rule before running paid traffic at scale.
  const attempts = new Map();
  function isLimited(req) {
    const time = now();
    for (const [key, bucket] of attempts) if (bucket.expires <= time) attempts.delete(key);
    const address = env.VERCEL === '1'
      ? String(req.headers['x-forwarded-for'] || 'unknown').split(',')[0].trim()
      : req.socket?.remoteAddress || 'local';
    const key = createHash('sha256').update(address).digest('hex');
    let bucket = attempts.get(key);
    if (!bucket) {
      if (attempts.size >= 2000) return true;
      bucket = { count: 0, expires: time + WINDOW_MS };
      attempts.set(key, bucket);
    }
    return ++bucket.count > 5;
  }

  return async function subscribe(req, res) {
    res.setHeader('Cache-Control', 'no-store');
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    res.setHeader('X-Content-Type-Options', 'nosniff');
    const reply = (status, message, ok = false) => {
      res.statusCode = status;
      res.end(JSON.stringify({ ok, message }));
    };
    if (req.method !== 'POST') {
      res.setHeader('Allow', 'POST');
      return reply(405, 'Please use the newsletter signup form.');
    }
    // Only our own browser forms; no wildcard CORS, user-supplied redirect or API URL.
    const allowed = new Set([SITE]);
    if (env.VERCEL_URL) allowed.add('https://' + env.VERCEL_URL);
    if (env.NODE_ENV !== 'production' && env.VERCEL !== '1') {
      allowed.add('http://127.0.0.1:8766');
      allowed.add('http://localhost:8766');
    }
    if (!allowed.has(req.headers.origin) || req.headers['sec-fetch-site'] === 'cross-site') {
      return reply(403, 'Please use the signup form on the fall guide.');
    }
    if (!/^application\/json(?:;|$)/i.test(req.headers['content-type'] || '')) {
      return reply(415, 'Please use the newsletter signup form.');
    }
    if (Number(req.headers['content-length'] || 0) > MAX_BODY) return reply(413, 'The request is too large.');
    let body;
    try {
      body = Buffer.isBuffer(req.body) ? req.body.toString('utf8') : req.body;
      if (typeof body === 'string') {
        if (Buffer.byteLength(body) > MAX_BODY) return reply(413, 'The request is too large.');
        body = JSON.parse(body);
      }
      if (!body || Array.isArray(body) || typeof body !== 'object') return reply(400, MESSAGES.invalid);
      if (Buffer.byteLength(JSON.stringify(body)) > MAX_BODY) return reply(413, 'The request is too large.');
    } catch (_) {
      return reply(400, 'Please check the form and try again.');
    }
    if (isLimited(req)) {
      res.setHeader('Retry-After', '600');
      return reply(429, MESSAGES.limited);
    }
    if (typeof body.website !== 'string' || body.website.trim()) return reply(400, MESSAGES.retry);
    const email = typeof body.email === 'string' ? body.email.trim() : '';
    if (email.length > 254 || !/^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$/.test(email)) return reply(400, MESSAGES.invalid);
    if (!['top', 'bottom'].includes(body.placement)) return reply(400, 'Please use the newsletter signup form.');
    const apiKey = env.beehiiv_api;
    const publicationId = env.beehiiv_pub_id;
    if (!apiKey || !/^pub_[0-9a-fA-F-]+$/.test(publicationId || '')) {
      logger.error('newsletter_signup_configuration_missing');
      return reply(503, MESSAGES.unavailable);
    }
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 8000);
    try {
      const upstream = await fetcher(`https://api.beehiiv.com/v2/publications/${publicationId}/subscriptions`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
        redirect: 'error',
        signal: controller.signal,
        body: JSON.stringify({
          email,
          reactivate_existing: false,
          send_welcome_email: true,
          double_opt_override: 'not_set',
          utm_source: 'fall_guide',
          utm_medium: 'website',
          utm_campaign: 'fall_guide_2026',
          utm_content: `newsletter_${body.placement}`,
          referring_site: SITE + '/'
        })
      });
      if (!upstream.ok) {
        // Log only fixed diagnostics/status codes, never addresses, credentials or response bodies.
        logger.error('newsletter_signup_upstream_error', { status: upstream.status });
        if (upstream.status === 429) {
          res.setHeader('Retry-After', '60');
          return reply(429, MESSAGES.limited);
        }
        return reply(502, MESSAGES.retry);
      }
      const result = await upstream.json();
      if (!result.data?.id || !['active', 'pending', 'validating'].includes(result.data.status)) {
        // Do not silently reactivate unsubscribed/suppressed addresses or claim they signed up.
        return reply(409, MESSAGES.retry);
      }
      return reply(200, MESSAGES.received, true);
    } catch (_) {
      logger.error(controller.signal.aborted ? 'newsletter_signup_timeout' : 'newsletter_signup_request_failed');
      return reply(502, MESSAGES.retry);
    } finally {
      clearTimeout(timeout);
    }
  };
}

module.exports = { createSubscribeHandler };
