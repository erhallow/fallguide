/* Vercel Web Analytics: enable Analytics in the guide's project before deploying.
 * Custom events require Pro/Enterprise. See docs/link-tracking.md.
 */
(function () {
  'use strict';
  // Local files, localhost and preview deployments must never pollute live reports.
  if (location.protocol !== 'https:' || location.hostname !== 'fallguide.nwiexplored.com') return;
  if (window.__fallGuideAnalytics) return;
  window.__fallGuideAnalytics = true;

  window.va = window.va || function () {
    (window.vaq = window.vaq || []).push(arguments);
  };

  if (!document.querySelector('script[src="/_vercel/insights/script.js"]')) {
    var script = document.createElement('script');
    script.defer = true;
    script.src = '/_vercel/insights/script.js';
    document.head.appendChild(script);
  }

  function recordLink(event) {
    if (event.defaultPrevented || event.isTrusted === false) return;
    if (event.type === 'click' ? event.button !== 0 : event.button !== 1) return;
    var target = event.target;
    if (target && !target.closest) target = target.parentElement;
    var link = target && target.closest('a[data-guide-section][data-guide-item][data-guide-link]');
    if (!link || !/^https?:\/\//i.test(link.getAttribute('href') || '')) return;
    try {
      // Two properties fit base Pro's limit. The item includes the link variant,
      // e.g. pumpkin-smash-bash__details versus gabis-arboretum__hours-and-admission.
      // No email, visitor ID, incoming query parameters or full URL is sent here.
      window.va('event', {
        name: 'guide_link_click',
        data: {
          section: link.dataset.guideSection,
          item: link.dataset.guideItem + '__' + link.dataset.guideLink
        }
      });
    } catch (_) {
      // Analytics must never block navigation, even if unavailable or blocked.
    }
  }

  document.addEventListener('click', recordLink);
  document.addEventListener('auxclick', recordLink);
})();
