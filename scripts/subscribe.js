(function () {
  'use strict';
  var forms = document.querySelectorAll('[data-subscribe-form]');
  forms.forEach(function (form) {
    var input = form.querySelector('[name="email"]');
    var button = form.querySelector('button[type="submit"]');
    var status = form.querySelector('[role="status"]');
    var busy = false;
    if (location.protocol === 'file:') {
      // Keep the local design preview clean; only the deployed endpoint can subscribe.
      return;
    }
    button.disabled = false;
    form.addEventListener('submit', async function (event) {
      event.preventDefault();
      if (busy) return;
      if (!input.checkValidity()) {
        status.textContent = 'Enter a valid email address.';
        status.classList.add('is-error');
        input.setAttribute('aria-invalid', 'true');
        input.focus();
        return;
      }
      input.removeAttribute('aria-invalid');
      busy = true;
      button.disabled = true;
      button.textContent = 'Subscribing…';
      form.setAttribute('aria-busy', 'true');
      status.textContent = '';
      status.classList.remove('is-error');
      var controller = new AbortController();
      var timeout = setTimeout(function () { controller.abort(); }, 12000);
      try {
        var response = await fetch('/api/subscribe', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'same-origin',
          signal: controller.signal,
          body: JSON.stringify({
            email: input.value.trim(),
            placement: form.dataset.subscribeForm,
            website: form.querySelector('[name="website"]').value
          })
        });
        var result = await response.json();
        if (!response.ok || result.ok !== true) {
          throw new Error(result.message || 'Signup is unavailable. Please try again shortly.');
        }
        status.textContent = result.message;
        button.textContent = 'Signup received';
        input.value = '';
        input.disabled = true;
        if (location.hostname === 'fallguide.nwiexplored.com' && typeof window.va === 'function') {
          try {
            // Accepted signup, not a confirmed double opt-in or a guaranteed new subscriber.
            window.va('event', { name: 'guide_signup_received', data: { section: 'newsletter-' + form.dataset.subscribeForm } });
          } catch (_) { /* Analytics must not change a successful signup. */ }
        }
      } catch (error) {
        status.classList.add('is-error');
        // Avoid showing network/parser internals; API messages are plain text, never HTML.
        status.textContent = error instanceof SyntaxError || error instanceof TypeError || error.name === 'AbortError'
          ? 'We couldn’t connect. Please try again shortly.'
          : error.message;
        button.textContent = 'Subscribe for free';
        button.disabled = false;
        busy = false;
      } finally {
        clearTimeout(timeout);
        form.removeAttribute('aria-busy');
      }
    });
  });
})();
