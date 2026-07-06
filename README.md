# Steve Ostermiller Advisory

One-page marketing site for **Steve Ostermiller Advisory** — operational excellence
for founder CEOs, without the overhead of a full-time COO.

Static HTML/CSS, no build step, deployed on GitHub Pages.

## Local preview

Always preview via a local server — opening `index.html` directly can appear
unstyled because the browser/preview sandbox may block the external stylesheet.

```bash
./serve.sh            # then open http://localhost:8010
```

## Structure

```
index.html              # the page (structure only)
assets/css/style.css     # all styling (single source of truth)
brand/                   # logo + favicon used by the site
  favicon.png            # SOa monogram (favicon)
  logo-wordmark.png      # square wordmark (used as social/OG image)
  LI banner.png          # LinkedIn banner (reference)
```

Brand font is **Crushed** (Google Fonts); brand color is the orange gradient
`#983f15 → #c55a29 → #f2763d`, sampled from the logo.

> **Note:** `brand/` also holds private source material (LinkedIn PDF, positioning
> notes). Those are git-ignored and never published — see `.gitignore`.

## Contact form

The contact section has an email button (works immediately) plus an optional form.
The form posts to [Formspree](https://formspree.io): create a free form and replace
`YOUR_FORM_ID` in `index.html`. Email address: `steve@ostermilleradvisory.com`.

## Deploy (GitHub Pages)

1. Push this repo to GitHub (`main` branch).
2. Repo **Settings → Pages → Build and deployment → Deploy from a branch**,
   select **`main` / `/ (root)`**, Save.
3. The site publishes at `https://<user>.github.io/<repo>/` within a minute or two.

### Custom domain (ostermilleradvisory.com)

When DNS is ready:

1. Add a `CNAME` file at the repo root containing `ostermilleradvisory.com`.
2. At your DNS host, point the apex domain to GitHub Pages
   (A records to `185.199.108–111.153`, and a `www` CNAME to `<user>.github.io`).
3. Settings → Pages → Custom domain → enter the domain, and enable
   **Enforce HTTPS** once the certificate is issued.
