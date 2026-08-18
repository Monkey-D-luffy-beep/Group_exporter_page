# Group Contacts Exporter — Landing Page

Marketing/SEO landing page for the **Group Contacts Exporter** Chrome extension (exports WhatsApp Web group members — name, country code, phone, role — to CSV, 100% local processing).

**Live:** https://groupexporter.nexoraai.co.in/
**Repo:** https://github.com/Monkey-D-luffy-beep/Group_exporter_page
**Deploy:** Vercel, connected to this repo — pushes to `main` auto-deploy.
**Chrome Web Store listing:** https://chromewebstore.google.com/detail/group-contacts-exporter-%E2%80%94/kmegeibfadlmgejfedidcamnbljekkkp

## Status: live, in maintenance/growth mode

Site is deployed, DNS pointed, indexed request submitted to Search Console (Domain property covering all of `nexoraai.co.in`, so no separate GSC verification was needed for this subdomain). Not yet done: passive — waiting on organic backlinks/reviews to accrue, nothing actionable blocking right now.

## Why static HTML (no framework)

Single marketing page — plain HTML/CSS/JS beats React/Vite here: zero JS framework payload (faster LCP, a real Google ranking factor), fully crawlable without JS execution, trivial to host anywhere.

## Structure

```
index.html            Full landing page — hero, how-it-works, features, privacy, FAQ, contact, CTA
privacy-policy.html    Required privacy policy (linked from CWS listing + footer)
css/style.css          All styling
js/script.js           Contact form (EmailJS + Turnstile) + footer year
assets/                icon.webp (real brand icon), favicon, banner-social.webp (OG image)
robots.txt / sitemap.xml
```

**No raster product screenshots.** The hero popup, extraction-progress state, CSV table, and "500+ members" stat are all live HTML/CSS recreations of the real extension UI (in `index.html`, classes `.app-mock`, `.csv-mock`, `.stat-mock`, `.shield-mock`) — not `<img>` screenshots. This was a deliberate switch: raster versions had a duplicate-headline/dead-space problem and a flexbox `align-items: stretch` bug that distorted them; the live version is crisper, has zero image weight, and is fully in CSS control. If you ever want real screenshots again, `Store Listing_files/` and the loose `1.png`–`5.png` in the repo root have the originals (untracked, not shipped).

## Contact form — how it actually works

- Submits via `emailjs.send()` in `js/script.js`, reusing the **same EmailJS account/service/template as the main nexoraai.co.in site** (no dedicated template for this project — deliberate shortcut). Submissions are tagged in `from_name` (`[Group Contacts Exporter] ...`) and prefixed in the message body so they're distinguishable from the main site's contact form in the same inbox.
- Protected by the **same Cloudflare Turnstile widget** as nexoraai.co.in (site key hardcoded in `js/script.js` — safe, Turnstile site keys are meant to be public). This domain had to be added to that widget's allowed-hostnames list in the Cloudflare dashboard for it to validate here.
- **Client-side verification only** — this site has no serverless backend, so there's no `api/contact.js`-style server-side Turnstile check like the Nexora site has. A determined attacker could bypass by calling EmailJS directly with the exposed public key. If that ever matters, the fix is adding a Vercel serverless function here (same pattern as `Nexora-AI-Website/api/contact.js`) and moving verification server-side.
- Both the EmailJS public key and Turnstile site key are hardcoded directly in `js/script.js` since this is a build-step-free static site — no `.env`/Vite injection mechanism exists here. That's fine for these two specific values (both are designed to be client-exposed); never add a real secret (an EmailJS *private* key or a Turnstile *secret* key) this way.

## SEO strategy (grounded in actual competitor research, not guessed)

A background research pass (Aug 2026) surfaced real, citable competitor weaknesses this page's copy leans on — factually, without naming competitors:
- **WAXP** (a top competitor): 3.1★ live rating, confirmed reviews complaining about a hidden 10-contact free-trial cap and silent data loss on larger exports.
- **WASendly**: requires Google sign-in even on its nominally free tier, and paywalls group-member extraction — the exact feature this product leads with.
- The most common "free" alternative people currently find is a browser DevTools/console-paste JavaScript snippet — genuinely intimidating for the non-technical personas (community admins, recruiters, real-estate agents) this targets.

This shaped: the proof-strip stats (`~2 hrs saved`, `1,000s of members — no 10-contact cap`, `0 console scripts`, `0 signups`), an 11-question FAQ using real search phrasing (`export whatsapp group members to excel`, `backup whatsapp group before leaving`, `whatsapp group members with country code`, etc. — verified as real search demand, not invented), and JSON-LD `FAQPage` + `SoftwareApplication` structured data kept in sync with the visible FAQ.

**Deliberately avoided:** fabricated testimonials/ratings (the extension has ~5 real CWS reviews not yet reflecting publicly, more incoming organically — no fake ones added to compensate) and named "vs. Competitor X" comparison content (two actual competitors run self-serving comparison blogs that rank themselves first — flagged in research as a pattern to avoid, not copy).

## Pricing language — handle with care

**A paid tier is planned** (not yet defined in scope). Copy was deliberately written to avoid "free forever" / permanent-free claims — check `index.html` for the FAQ pricing answer and proof-strip if/when the paid tier ships, since that copy will need a real update at that point (currently says pricing "may evolve," which is accurate today but is a placeholder, not a final answer).

## Local preview

No build step:
```bash
npx serve .
```
(Note: the `serve` package does its own `.html`-extension redirect behavior locally that doesn't happen on the real Vercel deploy — not a bug, just a local-dev-server quirk.)

## Loose files in repo root (untracked, not shipped)

`1.png`–`5.png`, `Store Listing.html`, `Store Listing_files/` — the original real CWS screenshots this page's live mockups were built from, plus a saved copy of the CWS listing page. Kept for reference; safe to delete if no longer needed, or keep for whenever the real UI changes and these need re-referencing.
