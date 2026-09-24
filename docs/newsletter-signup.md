# Newsletter signup

Both forms use the approved headline and subtext. The flow is:
email form → same-origin POST `/api/subscribe` → beehiiv → inline confirmation/error.
The site stays a static guide with one Node.js Vercel Function; no paid integration
service or new frontend framework is required.

## Vercel configuration before publishing

In the **fallguide project's** environment variables:

| Name (case-sensitive) | Value |
| --- | --- |
| `beehiiv_api` | The API key already added by the owner; must allow subscription creation |
| `beehiiv_pub_id` | NWI Explored's nonsecret ID beginning with `pub_`; the owner reports saving this in Vercel |

The owner has reported saving both variables in Vercel. The integration now uses
those exact names; their values and environment scopes have not been independently
verified. Do not paste API keys into chat or source code. Values are read only
inside the server function. Set the variables for Production; only use Preview
if intentionally testing against that publication. Redeploy after changing them.
The linked Vercel connector currently lists only `nwi-ultimate`, not this guide,
so its environment variables could not be verified from this task.

Vercel uses Node 24 (specified in `package.json`). There are no external npm
dependencies. The `/api` directory is detected by Vercel; this route does not run
through a static Python HTTP server or a `file://` preview. The local-file preview
disables submission without showing a preview notice. The compact CTA contains
only the approved headline, subtext, email field and subscribe button at rest.
Input labels remain available to screen readers; feedback appears inline only
after an attempted submission. The extra signup links and fine print were removed
at the owner's request; the footer's newsletter and sample-issue links remain.

## Subscription behavior

- Requests a welcome email using beehiiv's configured welcome email; it does not
  edit that email or create the previously tabled Meta/ManyChat workflows.
- Preserves publication-level double opt-in settings (`not_set`). Pending or
  validating signups are acknowledged as received, not falsely marked confirmed.
- Does not reactivate unsubscribed, paused, or suppressed addresses or incorrectly
  report those statuses as successful signups.
- Does not assign paid tiers or override newsletter-list defaults.
- Attributes subscriptions to `utm_source=fall_guide`, `utm_medium=website`,
  `utm_campaign=fall_guide_2026`, and `utm_content=newsletter_top` or
  `newsletter_bottom`. This identifies which signup form was used.
- Emits `guide_signup_received` to Vercel Analytics when the API accepts a signup,
  with only the form section. It is not a verified-new-subscriber conversion:
  existing subscribers and pending confirmations may also be accepted.
- No email addresses, API keys, upstream response bodies, or incoming query
  parameters are placed in analytics, URLs, browser storage, or application logs.

## Safety and abuse controls

POST-only JSON, strict origin allowlist, input/body-size validation, an offscreen
honeypot, upstream timeout, sanitized errors, and no-store responses are included.
The browser prevents repeat submissions while a request is pending and retains
the address after errors so readers can retry. Compact inline email validation
replaces the browser's native tooltip without removing server-side validation.
When JavaScript is disabled, an enable-JavaScript message appears; the footer's
newsletter link remains available.

Burst limiting allows five attempts per IP per ten minutes **per warm function
instance**. It is deliberately documented as best-effort, not distributed bot
protection; it resets across cold starts and does not coordinate across instances.
Before substantial paid traffic, configure a Vercel Firewall rate-limit rule for
POST `/api/subscribe`, or add shared rate limiting/CAPTCHA. No paid service or
account security settings were changed here. Keep the publisher's privacy notice
current and provide its verified URL if it should be linked beside these forms.

## Verification and publishing

Automated tests use mock credentials and responses only; no real subscriptions or
welcome emails are created. Run with Python 3 and Node 24:

```sh
python3 scripts/check-guide.py
python3 scripts/check-tracking.py
python3 scripts/tag_links.py --check
node --test scripts/check-analytics.cjs scripts/check-subscribe.cjs
```

For a safe browser test, run `node scripts/serve-signup-test.cjs` and open
`http://127.0.0.1:8766`. This server cannot contact beehiiv. It returns a simulated
failure for `fail@example.com`, pending confirmation for `pending@example.com`,
and a simulated accepted response for other valid test addresses. It logs status
and placement only, never the addresses.

After the correct Publication ID and Vercel variables are confirmed, deploy the
approved integration and have the owner submit an address they control. Verify
the subscriber, source attribution, and any confirmation/welcome email in beehiiv.
No end-to-end live subscription should be claimed before that check succeeds.

Reference: [beehiiv create-subscription API](https://developers.beehiiv.com/api-reference/subscriptions/create).

## Verification report — September 24, 2026

47 automated tests pass: 17 guide-content, 6 link-label, 9 analytics and 15 signup
checks. The browser was tested against the real local handler with a mocked
beehiiv boundary, not a production publication.

| Boundary | Evidence |
| --- | --- |
| UI renders | Both forms show the exact approved copy, labeled email inputs and buttons; no console warnings/errors or horizontal overflow in the tested desktop viewport. |
| Browser → handler | Top pending test and bottom retry reached `/api/subscribe`; correct placement logged without email addresses. |
| Handler → mocked beehiiv | Unit tests verify authorization, publication URL, settings and attribution. Browser mock logs confirm `newsletter_top` and `newsletter_bottom`. |
| Response → UI | HTTP 200 shows “Signup received”; simulated upstream 500 becomes sanitized HTTP 502; failed address remains visible and retry succeeds. |
| Live beehiiv | Not verified: the owner reports both variables are saved, but the connected Vercel account does not expose this project's settings. No real subscriber or welcome email was created. |

The first required live boundary remains configuration/credential verification
and an owner-approved signup after deployment. Automated tests do not establish
successful delivery to the production beehiiv publication.

Compact-CTA follow-up: both panels now place copy beside the form on desktop and
stack below 900px, with a 44px-minimum button. Extra notes, links and idle preview
text were removed. The updated 47-test suite passes; direct `file://` browser
preview was blocked by the browser URL policy, so the prior browser evidence
above does not establish visual verification of this revised layout.
