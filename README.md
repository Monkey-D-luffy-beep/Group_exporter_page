# Group Contacts Exporter — Landing Page

Static, dependency-free SEO landing page for the **Group Contacts Exporter** Chrome extension.

## Why static HTML (no framework)

This is a single marketing page, so plain HTML/CSS/JS was chosen over React/Vite:
- Zero build step, zero JS framework payload — fastest possible Core Web Vitals (LCP/CLS), which directly affects Google ranking.
- Fully crawlable without JS execution — no hydration required for search engines or link-preview bots.
- Trivial to deploy on any static host and point a subdomain at.

## Structure

```
index.html            Main landing page (hero, how it works, features, privacy, FAQ, CTA)
privacy-policy.html    Required privacy policy (linked from the CWS listing and footer)
css/style.css          All styling, single file
js/script.js           Minimal JS (footer year only — FAQ uses native <details>)
assets/favicon.svg     Favicon / brand mark
robots.txt / sitemap.xml
```

## Before going live

1. **Confirm the domain.** Meta tags, canonical URLs, sitemap, and structured data are currently set to `https://groupexporter.nexoraai.co.in/`. Update all occurrences if the final domain differs.
2. **Add a real Open Graph image** at `assets/og-image.png` (1200×630px) — referenced in `index.html` but not yet created.
3. **Swap the hero mockup for a real screenshot** of the extension popup/CSV output if you have one — the current hero visual is a CSS-built mockup, not a real screenshot.
4. **Point DNS**: create a `CNAME`/`A` record for `groupexporter` under `nexoraai.co.in` pointing at wherever you deploy (Vercel/Netlify/GitHub Pages/Cloudflare Pages all support static sites with zero config here).
5. **Submit the sitemap** (`/sitemap.xml`) to Google Search Console once live.

## Local preview

No build step — just open `index.html` in a browser, or serve the folder:

```bash
npx serve .
```

## Deploy (any static host)

- **Vercel**: `vercel` in this folder, or connect the repo and set no build command / output directory `.`.
- **Netlify**: drag-and-drop this folder, or connect the repo with publish directory `.`.
- **GitHub Pages**: push to a repo, enable Pages on the `main` branch root, and set a custom subdomain via a `CNAME` file (`groupexporter.nexoraai.co.in`) plus DNS.
