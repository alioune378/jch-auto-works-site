# JCH Auto Works — Website Project Guide
Prepared by Dalal Technologies · October 2026

## 1. Current-site assessment (jchautoworksllc.org, audited Oct 28, 2026)
- **Platform:** Duda/CCC template, one page plus Careers and Repair Authorization pages.
- **SEO:** title is just "J C H Auto Works LLC"; meta description "Auto Repair Facility". No city, no service keywords, no structured data, no service pages. Copyright still reads 2023.
- **Conversion:** one generic contact form (name/email/phone/message). No estimate flow, no photo upload, no click-to-call in the hero, no sticky mobile call bar.
- **Credibility:** strengths (family owned, 30+ years, I-CAR, lifetime warranty, insurance help) are buried in one paragraph and four cards. No shop photos, no reviews, LinkedIn icon links to linkedin.com (not a JCH page).
- **Navigation:** anchor links only; services are not individually findable by Google.

## 2. Design strategy (what we took from the national chains, without copying)
- Caliber / Gerber / CARSTAR all lead with **one action** (estimate or call), explain the **claim process step by step**, and give every service its own page. We kept those patterns.
- Where JCH wins: it's a **family shop with real people and real photos**. The design leans on the owner's actual shop photos instead of stock, and the copy speaks like the shop, not a franchise.
- Visual system: obsidian/midnight backgrounds, chrome silver, and the **electric blue from the JCH shield logo** for actions. The brief suggested signal red (#D63B35); we kept the logo's blue so the site matches the existing brand. Red is used only for form errors. Switch the `--blue` token in `assets/style.css` if the owner prefers red.
- Type: Barlow Condensed (body-shop decal feel), Manrope (reading), IBM Plex Mono (repair-order labels). The repair journey is styled as a repair order with real shop terms (teardown, supplement) explained in plain language.

## 3. Verified fact sheet (source: old website + owner photos)
| Fact | Value |
|---|---|
| Name | JCH Auto Works LLC (old site: "J C H Auto Works LLC") |
| Address | 904 State Route 21, Palmyra, NY 14522 (mail: PO Box 121) |
| Phone / email | (315) 584-1944 · JCHAutoWorks@yahoo.com |
| Hours | Mon–Fri 8:00–5:00, Sat–Sun closed |
| Ownership | Family owned and operated, "recently established" |
| Experience | "Over 30 years of auto body expertise" |
| Certification | "iCar-Certified technician" |
| Services | Free estimates, insurance assistance, lifetime warranty, PDR; FAQ adds cosmetic & structural repair, bumper, paint, windshield & glass, diagnostics & calibration |
| Insurance | "We work with all major insurance companies" |
| Warranty | Workmanship for as long as you own the vehicle; parts carry manufacturer warranty |
| Facebook | facebook.com/profile.php?id=61558594201120 |
| Signage (real storefront photo) | "Registered State of NY Motor Vehicle Repair Shop"; building number 904 |

**Photo provenance.** The storefront photo is a real photo of the shop. The two interior images (technician sanding a panel, repair bay) are AI-generated illustrations. On the site they are labeled "Illustrative image" wherever they appear, used only as mood/backgrounds, and never described as JCH's shop, staff or work. Replace them with real interior photos (section 9), then set `media.illustrative` to `false` in `src/site.json`.

## 4. Confirm with the owner before launch
All of these live in `src/site.json` with a `status` note. Items marked `show:false` are hidden until confirmed.
1. Whose "30+ years": the owner's personal experience or the team's combined? (Site wording: "our team brings more than 30 years".)
2. I-CAR: technician name and level (Platinum? ProLevel?) — we currently say only "I-CAR certified technician".
3. NYS DMV repair shop facility number (to show in the footer).
4. Year the LLC opened; owner's name, story and portrait for the About page and an owner message.
5. Glass: in-house or a partner installer? ADAS calibration: which are done in-house vs. sublet?
6. Structural: frame machine / measuring system brand (only name it once confirmed).
7. Towing and rental: does JCH arrange either? (Site currently says "call us, check your policy".)
8. Written warranty terms and exclusions.
9. Service area towns (currently: Macedon, Newark, Marion, Walworth, Ontario, Fairport, Victor, Wayne County).
10. Repair Authorization page on the old site: still needed? Currently redirected to /contact.
11. The second sign in the exterior photo: is JCH an NYS inspection station?
12. Approval of the repair process steps shown on the homepage.
13. Real interior photos to replace the two illustrations (bays, paint area, technicians at work with signed releases).
14. "Works with all major insurance companies", the warranty wording and the services list come from the shop's own former website. Have the owner reconfirm each before launch.

## 5. What's in the build
- 18 pages: Home, Services hub, 6 service pages, About, Insurance, Our Work (portfolio coming soon), Reviews, Estimate, Fleet & Business, FAQ, Contact, Privacy, 404.
- **Estimate flow:** 4 steps (vehicle → damage & photos → insurance & timing → contact), VIN check, conditional insurance and not-drivable fields, up to 6 photos with previews, phone-size downscaling, upload progress, real error messages, consent, preliminary-estimate disclaimer. No policy/claim numbers collected.
- **Business inquiry form** and a **contact form**.
- Mobile: compact header that shrinks on scroll; menu with collapsible Services list and one estimate button; Call / Free Estimate bar that appears only after the page's own buttons scroll away and hides over the footer and while typing; live "Open now" indicator in shop time.
- Tested Oct 28, 2026 at 390, 768 and 1366 px: no horizontal overflow or header overlap on any page; estimate, fleet and contact forms validate, show errors, accept photos, and reach the confirmation step (preview mode).
- SEO: unique titles (≤ 60 characters) and descriptions (≤ 160), one H1 per page, no broken internal links, every image with alt text and dimensions, canonical URLs, Open Graph, `AutoBodyShop` + `BreadcrumbList` + `Service` + `FAQPage` JSON-LD, sitemap.xml, robots.txt, 301s from old URLs. No review/rating schema (no real reviews yet). No city doorway pages.
- Accessibility: skip link, visible focus, keyboard-operable menu/tabs/slider, labeled fields, `aria-invalid` errors, reduced-motion support.
- Analytics hooks: click-to-call, directions, email, CTA and form-step events pushed to `dataLayer`; GA4/GTM load only after cookie consent and only when IDs are set.

## 6. Deploy (GitHub + Netlify)
1. Create repo (e.g. `alioune378/jch-auto-works`) and push this folder.
2. Netlify → Add new site → Import from GitHub. `netlify.toml` already sets build `cd src && python3 build.py`, publish `dist`.
3. **Forms:** Netlify → Site configuration → Forms → Enable form detection, then redeploy. Add email notifications for `estimate`, `fleet` and `contact` → JCHAutoWorks@yahoo.com (Forms → Form notifications).
4. Test one real submission with photos on the `.netlify.app` URL (forms go live automatically on Netlify and on jchautoworksllc.org; everywhere else they run in labeled preview mode).
5. Domain: point jchautoworksllc.org DNS to Netlify only after the owner approves; HTTPS is automatic.
6. Submit `sitemap.xml` in Google Search Console.

**To edit content:** change `src/site.json` (facts, hours, reviews, gallery pairs) or copy in `src/build.py`, commit, Netlify rebuilds.

## 7. Integrations & credentials needed
| Need | From | Where it goes |
|---|---|---|
| Domain DNS access | Owner's registrar | Netlify domain settings |
| Netlify Forms (check the account plan's monthly submission and file-upload allowance; photo uploads count) | Netlify | — |
| Notification email confirmation | JCHAutoWorks@yahoo.com | Netlify form notifications |
| GA4 Measurement ID | Google Analytics | `site.json → integrations.ga4Id` |
| Search Console verification | Google | `site.json → integrations.searchConsoleToken` |
| Google Business Profile access + review link | Owner | `site.json → reviews.googleReviewUrl` |
| Optional later: CRM (HubSpot free / Jobber), SMS, online booking | — | Not built; proposed only |

Lead tracking at launch: Netlify's Forms inbox (searchable, CSV export, spam filter + honeypot). A status pipeline (new → contacted → estimated → repaired) is a Phase 2 CRM item.

## 8. Local SEO & content plan
**Primary keywords (candidates; validate volume in Search Console after 60 days):** collision repair Palmyra NY · auto body shop Palmyra NY · body shop Wayne County NY · paintless dent repair Wayne County · dent repair Palmyra · car paint repair Palmyra · frame repair near Palmyra · auto glass Palmyra · insurance collision repair Palmyra.
**Mapping:** home → collision repair / auto body shop Palmyra; each service page → its keyword; insurance page → claim questions; contact → "near me" + directions.
**Google Business Profile:** primary category *Auto body shop*; add *Paintless dent repair service*, *Auto glass shop*; hours matching the site; the three real photos plus weekly new ones; services list matching the site's six; the estimate page as the booking link.
**Citations (same name/address/phone everywhere):** Google, Apple Business Connect, Bing Places, Yelp, Facebook, BBB, Palmyra/Wayne County chamber listings, the town's business directory (palmyrany.gov/businesses).
**Reviews:** ask every customer at pickup; text the Google review link the same day. Never incentivize, never fabricate.
**Articles (one per month):** What to do after a car accident in New York · How collision estimates and supplements work · What paintless dent repair can and can't fix · Why your car may need calibration after a windshield or bumper repair · Questions to ask before choosing a body shop · Deer collisions in Wayne County: what to do.

## 9. Photo checklist for the owner
Shop exterior (sunny, wide + sign) · office/reception · each bay (clean, lit) · paint booth & mixing area · frame/measuring equipment · technicians at work (signed photo release) · owner portrait · team photo · I-CAR certificate & DMV registration · 6–10 before/after pairs from the same angle (customer permission, plates hidden) · work-in-progress shots. Landscape, phone at chest height, no flash indoors.

## 10. Launch checklist
- [ ] Owner confirms items in section 4; update `site.json`
- [ ] Netlify form detection on; notifications to shop email; test submissions (with photos) received
- [ ] Owner approves all copy and photos
- [ ] GA4 + Search Console IDs added; consent banner tested
- [ ] DNS switched; HTTPS active; old URLs redirect
- [ ] Sitemap submitted; GBP website link updated to new pages
- [ ] Lighthouse mobile run on live URL (targets: LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1) — not yet measured on production

## 11. 30 / 60 / 90 days
- **30:** launch; GBP fully optimized; 5 core citations fixed; review-request habit at pickup; first photo shoot; real before/after pairs added.
- **60:** first two articles; owner story and portrait on About; check Search Console queries and adjust titles; first 10 Google reviews added to the site with permission.
- **90:** review form conversion (calls + estimates per week); decide on CRM/booking; add fleet case notes if JCH signs commercial accounts; consider a separate PDR or glass landing push based on real query data.
