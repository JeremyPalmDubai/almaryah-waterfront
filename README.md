# Al Maryah Waterfront

Multilingual property website: English, French, Spanish, Dutch, German and Portuguese. 66 HTML pages, 60 Tally forms, responsive brochure imagery, local fonts, brochure PDF and XML sitemaps.

## Deploy on Hostinger

Use **Deploy Web App → Import Git Repository** and select this public repository.

| Setting | Value |
| --- | --- |
| Framework | Vite |
| Branch | main |
| Root directory | / |
| Node.js | 24 |
| Build command | npm run build |
| Output directory | dist |

No environment variables or database are needed. Deployment requires a Hostinger plan supporting web apps. Canonical URLs use `https://almaryahwaterfront.com`; connect that domain and enable HTTPS in the hosting dashboard. A successful build does not configure DNS or certificates.

## Local development

```sh
npm install
npm run dev
npm run build
npm run preview
```

All pages are real HTML documents. Vite builds the complete page tree; there is no single-page application routing fallback. Shared images, fonts, scripts, brochure and sitemaps are in `public/`.

## Lead form and brochure

Uses the official Tally widget, form `44gVeA`. The brochure link is shown after a validated Tally submission event. The PDF is a public static asset, not an authenticated download. No lead data is stored in this repository. Do not send fake production submissions for testing.

## Content status

Starting prices describe categories, not confirmed prices for every variant. Missing unit prices are on request. Handover and payment schedule require written confirmation; visa eligibility is not guaranteed. Site operator identity and contact details remain to be completed in the legal/privacy pages. Tally's questions are currently English.

Images and logos originate from the supplied project brochure. Brand and media rights remain with their respective owners; this repository does not grant a license to those assets.

## Centralized content

Prices, FX, handover and payment data live in `content-source/project.json`. Localized copy lives in `content-source/content.py` and `types_content.py`. After editing these files, run `python3 regenerate.py` and commit the regenerated HTML and sitemaps. Python is not required on Hostinger; production uses the committed HTML and the Vite build.
