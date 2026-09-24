/* Offline browser-event tests. No requests are sent to Vercel. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { test } = require('node:test');

const source = fs.readFileSync(path.join(__dirname, 'link-analytics.js'), 'utf8');

function boot({ hostname = 'fallguide.nwiexplored.com', protocol = 'https:', existing = false, va } = {}) {
  const listeners = {};
  const scripts = [];
  const window = va ? { va } : {};
  const document = {
    querySelector: () => existing ? {} : null,
    createElement: () => ({}),
    head: { appendChild: script => scripts.push(script) },
    addEventListener(type, handler) {
      (listeners[type] ||= []).push(handler);
    }
  };
  const context = vm.createContext({ window, document, location: { hostname, protocol } });
  vm.runInContext(source, context);
  return {
    window, scripts, listeners,
    repeat: () => vm.runInContext(source, context),
    events: () => JSON.parse(JSON.stringify(Array.from(window.vaq || [], args => Array.from(args)))),
    click(overrides = {}, linkOverrides = {}) {
      const link = {
        getAttribute: () => 'https://fofarms.com/harvest-season/pumpkin-smash-bash/?utm_source=nwi_explored',
        dataset: {
          guideSection: 'harvest-festivals-and-fall-outings',
          guideItem: 'pumpkin-smash-bash', guideLink: 'details'
        },
        ...linkOverrides
      };
      const event = {
        type: 'click', button: 0, isTrusted: true, defaultPrevented: false,
        target: { closest: () => link },
        preventDefault: () => assert.fail('Must not block navigation'),
        stopPropagation: () => assert.fail('Must not intercept page interactions'),
        ...overrides
      };
      for (const listener of listeners[event.type] || []) listener(event);
    }
  };
}

test('loads one production Vercel script and installs listeners once', () => {
  const page = boot();
  page.repeat();
  assert.equal(page.scripts.length, 1);
  assert.equal(page.scripts[0].src, '/_vercel/insights/script.js');
  assert.equal(page.scripts[0].defer, true);
  assert.equal(page.listeners.click.length, 1);
  assert.equal(page.listeners.auxclick.length, 1);
});

test('never loads analytics or attaches tracking on local files, localhost or previews', () => {
  for (const location of [
    { hostname: '', protocol: 'file:' },
    { hostname: 'localhost', protocol: 'http:' },
    { hostname: '127.0.0.1', protocol: 'http:' },
    { hostname: 'fallguide-preview.vercel.app' },
    { protocol: 'http:' }
  ]) {
    const page = boot(location);
    page.click();
    assert.equal(page.scripts.length, 0);
    assert.deepEqual(page.events(), []);
    assert.deepEqual(Object.keys(page.listeners), []);
  }
});

test('records one event with exactly two nonpersonal reporting properties', () => {
  const page = boot();
  page.click();
  assert.deepEqual(page.events(), [['event', {
    name: 'guide_link_click',
    data: { section: 'harvest-festivals-and-fall-outings', item: 'pumpkin-smash-bash__details' }
  }]]);
});

test('keyboard and modified clicks work without interfering with navigation', () => {
  const page = boot();
  page.click({ detail: 0 });
  page.click({ ctrlKey: true });
  page.click({ metaKey: true });
  page.click({ shiftKey: true });
  assert.equal(page.events().length, 4);
});

test('middle-click records once; right-click and nonprimary click do not', () => {
  const page = boot();
  page.click({ type: 'click', button: 1 });
  page.click({ type: 'auxclick', button: 1 });
  page.click({ type: 'auxclick', button: 2 });
  assert.equal(page.events().length, 1);
});

test('ignores cancelled, synthetic, internal, phone and nonlink interactions', () => {
  const page = boot();
  page.click({ defaultPrevented: true });
  page.click({ isTrusted: false });
  page.click({ target: { closest: () => null } });
  page.click({ target: null });
  for (const href of ['#p2', 'tel:+12198652274', 'mailto:hello@example.org', 'javascript:void(0)']) {
    page.click({}, { getAttribute: () => href });
  }
  assert.deepEqual(page.events(), []);
});

test('nested text targets resolve to their link', () => {
  const page = boot();
  const link = {
    getAttribute: () => 'https://example.org/map?private=never-sent',
    dataset: { guideSection: 'fall-color-walks-and-hikes', guideItem: 'trail', guideLink: 'map' }
  };
  page.click({ target: { parentElement: { closest: () => link } } });
  assert.equal(page.events()[0][1].data.item, 'trail__map');
  assert.equal(JSON.stringify(page.events()).includes('private'), false);
});

test('existing Vercel function and script are reused', () => {
  const calls = [];
  const va = (...args) => calls.push(args);
  const page = boot({ existing: true, va });
  page.click();
  assert.equal(page.scripts.length, 0);
  assert.equal(page.window.va, va);
  assert.equal(calls.length, 1);
});

test('an unavailable analytics client cannot break a link', () => {
  const page = boot({ va: () => { throw new Error('blocked'); } });
  assert.doesNotThrow(() => page.click());
});
