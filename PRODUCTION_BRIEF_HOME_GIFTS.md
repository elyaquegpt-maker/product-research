# Production Brief: Wall Art, Ornaments, Desk Mats and Blankets (Etsy × Printify, October 2026)

This brief is for the design and production team. It goes deeper on products #3–#5 from [ETSY_PRINTIFY_DEEP_DIVE.md](ETSY_PRINTIFY_DEEP_DIVE.md): what to design, how to build the files, what to charge, and what to list first.

**How to read it.** Every design idea is tagged with the evidence behind it:
- **[Data]**: a third-party sales tracker (EtsyHunt) or keyword tool shows it selling. These are estimates, not Etsy's own figures.
- **[Etsy]**: Etsy's official trend reports or Color/Texture of the Year.
- **[Market]**: it shows up repeatedly on Etsy bestseller pages or in POD-vendor guides, but without sales numbers.
- **[Judgment]**: my recommendation, based on the pattern. Test these with small batches first.

No source publishes Etsy's actual best-selling images. The closest proxies are EtsyHunt's estimated weekly-sales rankings, Etsy's "Bestseller" badges and review counts, and vendor guides. Validate every keyword in eRank or Marmalead before you scale a design.

---

## 0. What the research changes

1. **Personalization is the main reason these items sell.** EtsyHunt's #1 estimated wall-art seller in September 2026 was a *custom felted farm animal nursery print with the baby's name*, at about 202 sales a week and $49k total revenue **[Data]**. Family name ornaments are called 2026's strongest ornament seller **[Market]**. Etsy says shoppers are "stepping away from AI-overload" toward items that feel personal **[Etsy]**.
2. **Textile and "stitched" looks are the 2026 aesthetic.** Etsy's "Soft Stitch Era" names crochet, embroidery and stitched textures **[Etsy]**. Merchize's 2026 ornament list opens with an *embroidered hoop ornament* **[Market]**, and the #1 wall-art seller is a *felted* look **[Data]**. You can print a stitched or felted texture with sublimation and UV printing. **This is the single most useful design direction in this brief.**
3. **Sets beat single items.** Nursery and gallery-wall buyers purchase **3–6 matching prints** per order **[Market]**. Design in collections, not one-offs.
4. **Correction to the first report: blankets.** Etsy grandma blankets cluster at **$25–50, median about $50**, and many listings run constant "sales" ($54.75 listed, $27.37 sale) **[Data]**. Amazon photo blankets sell at $11.99 **[Data]**. At a realistic **$54.99** a 50×60 sherpa earns **about $14.50 a sale, not $28**. Plain photo collages are a price war, so sell **designed** blankets instead. The calculator and the first report are now updated.
5. **Physical wall art competes with $5–15 digital downloads.** A plain unframed print has to give a buyer a reason to pay more: personalization, a matching set, or a **framed, ready-to-hang** version. The framed poster earns the most per sale in the whole catalog ($18, or $25 on Premium).

---

## 1. Profit per sale at recommended prices

From `etsy_printify.py` (Printify Free plan; Premium adds 20% off base). Etsy fees are 6.5% transaction plus 3% + $0.25 processing plus a $0.20 listing fee. Shipping is built into the price. Shipping costs, the 18×24 poster base and the ornament 3-pack base are estimates; check live Printify rates.

| Product | Price | Profit | Margin | If an offsite ad drove it | Premium profit |
|---|---:|---:|---:|---:|---:|
| Framed poster, small (Roma Imaging) | $69.99 | **$18.00** | 25.7% | $7.50 | $25.18 |
| Ornament 3-pack, personalized (base ~$12 est.) | $39.99 | **$18.74** | 46.9% | $12.74 | $21.14 |
| Sherpa blanket 50×60 | $54.99 | **$14.53** | 26.4% | $6.28 | $19.49 |
| Desk mat 31.5×15.5 | $34.99 | **$14.05** | 40.1% | $8.80 | $16.18 |
| Matte poster 18×24 | $34.99 | **$12.72** | 36.3% | $7.47 | $15.12 |
| Ceramic ornament, personalized | $21.99 | **$10.02** | 45.6% | $6.72 | $11.01 |
| Matte poster 12×18 | $24.99 | **$8.17** | 32.7% | $4.42 | $9.87 |
| Matte poster 8×10 | $16.99 | **$5.47** | 32.2% | $2.92 | $6.46 |
| Sherpa blanket at $49.99 | $49.99 | $10.00 | 20.0% | $2.50 | $14.96 |
| Framed poster at $59.99 | $59.99 | $8.95 | 14.9% | −$0.05 | $16.13 |

**Pricing rules:**
- **Ornaments: $21.99 personalized, not $16.99.** The extra $5 almost doubles profit, and personalized ornaments sell at $15–40 **[Market]**.
- **Posters: lead with 18×24 and framed.** The 8×10 earns too little per sale on its own. Keep it as the cheap entry size in a variation dropdown.
- **Framed: never below $64.99.** At $59.99, a sale driven by an offsite ad loses money.
- **Blankets: $54.99 floor.** Don't follow competitors into $25 "sale" prices.

---

## 2. Wall art (Printify matte posters, framed posters, canvas)

### Product setup
| Item | Printify product | Sizes to offer | Price ladder |
|---|---|---|---|
| Unframed print | Matte Vertical / Horizontal Poster | 8×10, 12×18, 18×24, 24×36 | $16.99 / $24.99 / $34.99 / $44.99 |
| Framed print | Framed Vertical Poster (Roma Imaging, from $35.89) | small, medium | $69.99 / $89.99 |
| Canvas (test later) | Matte Canvas, Stretched 1.25" | 12×16, 16×20 | price after checking live USD base |

### File specifications
- **300 DPI** at final size for posters. 150 DPI is the technical minimum, and prints look soft at that level **[Market]**.
- **Build one master file per aspect ratio** so a single design covers every size:
  - **2:3** master at **7200×10800 px** covers 24×36, 12×18 and 4×6.
  - **3:4** master at **5400×7200 px** covers 18×24 and 12×16.
  - **4:5** master at **4800×6000 px** covers 16×20 and 8×10.
- Keep text and faces **at least 0.5 in from every edge**. Framing covers the edges, and the crop differs between ratios.
- Canvas gallery wrap: add **1.5 in of bleed** on each side (+450 px at 300 DPI) **[Market]**.
- Export as sRGB PNG. Never upload a "web" export from Canva, a screenshot, or a 72 DPI JPG **[Market]**.

### Designs to produce (priority order)

**Personalized: the core of the wall-art line**

| # | Design | Personalization fields | Look | Evidence |
|---|---|---|---|---|
| W1 | **Felted / stitched nursery animals with the baby's name.** Farm and woodland sets: lamb, cow, duck, fox, bunny, bear. | Name, optional birth date | Soft felt texture, cream background, sage / oat / dusty blue | **[Data]** #1 EtsyHunt wall-art seller · **[Etsy]** Soft Stitch |
| W2 | **Nursery gallery set of 3 or 6.** Animals plus a name print as one listing. | Name | Same palette as W1 | **[Market]** buyers order 3–6 matching prints |
| W3 | **Birth stats print** | Name, date, time, weight, length, city | Minimal type and one small felted animal | **[Market]** |
| W4 | **Wedding or first-home location map** with coordinates | Names, date, city, coordinates | Map in **Patina Blue** with a **washed-linen** paper texture | **[Market]** · **[Etsy]** 2026 color and texture |
| W5 | **Family name sign, "Est. 2026"** | Family name, year | Serif type, linen texture, sage or terracotta accent | **[Market]** |
| W6 | **Couple portrait from photo** | Photo upload, names, date | Line art or simple flat illustration | **[Data]** in EtsyHunt's top 8 · ⚠ every order needs hand drawing |
| W7 | **Pet breed line art and name (no photo)** | Pet name, choose from 40–60 pre-drawn breeds | Single-line drawing, minimal | **[Judgment]** avoids per-order drawing and saturated AI portraits |

**Collections: no personalization, sold as sets**

| # | Collection | Look | Evidence |
|---|---|---|---|
| W8 | **Muted watercolor botanicals** (set of 3 and 6) | Cream, sage, warm beige | **[Market]** botanicals are evergreen; "quiet luxury" muted palette for 2026 |
| W9 | **Dark botanicals / whimsigoth**: moths, moons, night florals | Deep green, black, antique gold | **[Market]** "whimsigoth" searches high, moderate competition; Gothmas crossover |
| W10 | **Original fantasy world maps** in an antique-map style | Parchment, sepia, hand lettering | **[Data]** an LOTR map canvas is #2 on EtsyHunt. ⚠ **Never use Middle-earth or any franchise.** Invent your own world, or restore a confirmed public-domain antique map. |
| W11 | **Maximalist retro / 70s type prints** | Dense, layered compositions; burnt orange, mustard, brown | **[Market]** Gelato names maximalist retro as the emerging 2026 poster trend |
| W12 | **Supper club / vintage Italian kitchen**: cocktail recipes, lemons, pasta shapes | Vintage illustration, cream and red | **[Etsy]** "Supper Club" and "Nonna" trends · **[Market]** "vintage Italian art prints" keyword |
| W13 | **Patina Blue abstracts** (set of 2 or 3) | Blue-copper patina, linen texture | **[Etsy]** 2026 Color of the Year, "blue copper" searches up more than 3x |
| W14 | **Hobby niche sets**: mahjong tiles, birding field-guide plates, pickleball | Vintage-scientific plate style | **[Market]** mahjong demand is up while merchandise is still thin |

**Skip:** generic motivational quotes and "Live Laugh Love" type **[Market: saturated]**. Also skip anything in a franchise, brand or celebrity's look.

### Listing photos (shoot list for every listing)
1. **Hero:** a framed print on a styled wall, vertical 4:5 or 3:4. This is the search thumbnail, so make it readable at about 570×456 px **[Market]**.
2. Close-up of the texture (felt, paper, stitch detail).
3. **Scale shot** showing the print next to a sofa or crib, with sizes labeled.
4. Gallery-wall shot showing the full set.
5. **Personalization example** with every field filled in, plus a "How to personalize" graphic.
6. Size chart image listing every size.
7. Frame options (black, white, oak) if you sell the framed version.
8. Optional: a 5–10 second video panning across the room.

Etsy allows 10 images and 1 video per listing. Images should be at least 2000 px on the shortest side **[Market]**.

---

## 3. Ornaments (Printify ceramic, 1 / 3 / 5 / 10-piece)

**Timing is urgent.** Today is October 13. Couples, pet and name ornament searches spike from **October through December** **[Market]**. Printify production takes 2–7 business days and shipping adds more. **Every ornament listing below should be live by October 20**, and set your Etsy holiday ordering deadline from Printify's published cutoffs.

### Product setup
- **Printify Ceramic Ornament** (from $4.93; 1/3/5/10-piece packs exist). Shapes: **circle 2.99×2.99 in, heart 3.23×3.19, star 3.19×3.11, snowflake 2.64×2.99**, about 0.12 in thick, printed on **both sides** with sublimation **[Market: Printify size guide]**.
- Offer **shape as a variation** (circle / heart / star), so one listing covers three products.
- Acrylic photo ornaments sell around **$10–20** and are crowded (31,000+ photo-ornament listings) **[Market]**. Use them only for W-style designed photo layouts, not bare photos.

### File specifications
- Use Printify's template for each shape, and design at **at least 900×900 px per side** (3 in at 300 DPI). Larger is better.
- **Lines at least 5 px thick**, because fine detail is lost on a small print area **[Market: Printify help center]**.
- Keep text **at least 0.3 in from the hanging hole** at the top, and at least 0.15 in from every edge.
- **Back side:** "Christmas 2026" plus a small motif. It costs nothing extra and makes the ornament feel more finished.
- **Text layers** must be set up for Printify personalization. Name each layer to match its Etsy personalization field. Etsy allows a maximum of 5 personalization questions.

### Designs to produce (priority order)

| # | Design | Front | Back | Personalization | Evidence |
|---|---|---|---|---|---|
| O1 | **Family name ornament** | Names stacked or inside a tree / wreath shape, 2–10 names | "The [Surname]s · Christmas 2026" | Surname, up to 10 names | **[Market]** "2026's strongest seller" |
| O2 | **Faux-embroidery hoop ornament** | Printed stitched texture inside a wooden-hoop rim, with initial or name | Stitch-texture pattern | Name or initial | **[Market]** #1 on Merchize's list · **[Etsy]** Soft Stitch |
| O3 | **First Christmas married / together 2026** | Two names, heart, date | "Our First Christmas · 2026" | Names, wedding date | **[Market]** search spike for "Our First Christmas Together" |
| O4 | **First Christmas in our new home 2026** | House illustration (pick from 6 house styles) with family name | City and year | Family name, city, house style | **[Data]** EtsyHunt #2 is a "First Christmas in our new home" keepsake |
| O5 | **New-home map ornament** | Street map of the city or neighborhood, heart on the location | Address or coordinates and year | City, coordinates | **[Market]** map ornaments are "the least crowded niche" |
| O6 | **Baby's first Christmas 2026** | Felted or stitched animal (match W1) with the name | Birth date and weight | Name, date | **[Market]** milestone ornaments sell at $15–40 |
| O7 | **Pet ornament: breed and name** | Breed illustration from the W7 library, name, "2026" | Paw print and "Good boy / girl" | Name, breed | **[Market]** pet ornaments are big · **[Judgment]** breed library beats photo portraits |
| O8 | **Pet memorial** | Paw print, name, "Forever in our hearts" | Life dates | Name, years, optional photo upload | **[Market]** a big share of pet-ornament listings |
| O9 | **Nonna's / Grandma's Christmas** | Vintage kitchen illustration with "Nonna" or "Grandma" | Grandkids' names | Title, up to 6 names | **[Etsy]** "Grandma's Christmas" and "Nonna Holiday" trends |
| O10 | **Gothmas** | Dark florals, black and antique gold | Name | Name | **[Market]** Gothmas ornaments sell at $25–35 |
| O11 | **Group packs**: teacher, coworker, bridesmaid (3, 5 or 10-piece) | One design, different name on each piece | Year | Names list | **[Judgment]** larger orders per buyer |

**America 250:** 2026 is the US 250th anniversary, and vendor guides list it as an ornament niche **[Market]**. "America250" branding may be protected, so use generic wording such as "1776–2026" and check with the USPTO before listing.

### Listing photos
1. Hero: the ornament hanging on a softly lit tree, close and in focus.
2. Both sides side by side.
3. In a hand, to show the 3-inch size.
4. Personalization example plus a "How to order" graphic.
5. Shape options (circle / heart / star).
6. Gift box or a stack of several ornaments.

---

## 4. Desk mats (Printify Desk Mat, Classic 31.5×15.5 in)

Desk mats are mostly a **dorm, cubicle and gamer gift**: "dorm gift" and "cubicle decor" appear repeatedly in bestseller titles **[Market]**. They sell all year, with peaks in **back-to-school (Aug–Sep)** and **Q4**.

### File specifications
- Classic size **31.5×15.5 in** (Printify's custom desk mat page) **[Market]**. Check the live template, since other sizes exist.
- At 300 DPI that is **9450×4650 px**. 150 DPI (**4725×2325 px**) is acceptable for large items **[Market]**.
- **Composition rule [Judgment]:** a keyboard covers the center and a mouse covers the right third. Put the subject **on the left third and along the top edge**, and keep the middle a quieter pattern. Keep everything important **0.5 in from the stitched edge**.

### Designs to produce (priority order)

| # | Design | Look | Evidence |
|---|---|---|---|
| D1 | **Dark autumn florals** | Deep red, mustard and forest-green flowers on black | **[Market]** a dark autumn floral mat with thousands of reviews appears on several bestseller pages |
| D2 | **Celestial whimsigoth**: moon phases, stars, moths | Navy or black with antique gold | **[Market]** listed as "Top Selling Item" in Etsy titles; whimsigoth searches growing |
| D3 | **Watercolor cottage**: mushrooms, butterflies, wildflowers | Soft watercolor | **[Market]** cottagecore bestseller pages |
| D4 | **Original fantasy world map** (same world as W10) | Parchment, compass rose | **[Market]** map mats sell; ⚠ no game or franchise maps |
| D5 | **Kawaii pastel sky**: clouds and stars | Pink, lilac, baby blue | **[Market]** |
| D6 | **Koi pond / Japandi landscape** | Ink-wash, minimal | **[Market]** |
| D7 | **Art Nouveau florals** (your own work in the style) | Curving lines, muted gold | **[Market]** |
| D8 | **Patina Blue texture with name** | Blue-copper texture, small monogram bottom-left | **[Etsy]** Color of the Year · **[Judgment]** personalization upsell |
| D9 | **Hobby mats**: mahjong, birding, crochet pattern | Vintage plate or pattern style | **[Judgment]** low-competition niches |

**Personalization upsell:** a small name or gamertag in a corner for **+$5**. Set it up as one optional Etsy field.

**Listing photos:** a full desk setup with keyboard, mouse and monitor; a close-up of the stitched edge; the rubber back; a size comparison with a keyboard; and a dorm or cubicle lifestyle shot.

---

## 5. Blankets (Printify Sherpa Fleece 50×60; test Velveteen Plush)

### Product setup
- **Sherpa Fleece Blanket** (from $24.79) is the main product. **Velveteen Plush** (from $13.64 at the smallest size) is a lower-cost alternative to test, priced at **$44.99**.
- Sizes go from 30×40 (baby) to 60×80 (bed). Lead with **50×60**.
- **Price $54.99.** Don't follow the $25 fake-sale crowd. Compete on design, personalization and good photos **[Data]**.

### File specifications
- **150 DPI is acceptable** for blankets **[Market]**. That's **7500×9000 px** for 50×60. Use 200 DPI if you can.
- Keep text **2 in from the edges**, because fleece edges fold and roll. Make type larger than looks necessary on screen, since the print softens on plush fabric.

### Designs to produce (priority order)

| # | Design | Personalization | Evidence |
|---|---|---|---|
| B1 | **"Grandma's garden" birth-flower blanket**: one birth-month flower per grandchild, with names | Title (Grandma / Nana / Mimi), up to 10 names with birth months | **[Market]** a "First Mom Now Grandma Birth Flowers Blanket" sells across marketplaces; "grandma blanket" median $50 |
| B2 | **Letter to Mom / Grandma**: a long heartfelt letter set in elegant type | Recipient title, sign-off names | **[Judgment]** common POD format; no sales data found |
| B3 | **Pet memorial blanket**: photo upload in a designed frame, "Forever by your side", life dates | Photo, name, years | **[Market]** memorial blankets present, no sales numbers |
| B4 | **Designed family photo collage**: 6 or 9 photos with family name and "Est." | Photos, family name, year | **[Data]** a big category, but a price war. Win with a layout that looks designed, not a plain grid. |
| B5 | **Felted nursery baby blanket**, 30×40 (matches W1 and O6) | Baby name | **[Data]** EtsyHunt tracks a personalized baby-blanket bestseller list · **[Judgment]** cross-sell with W1 |
| B6 | **Patina Blue / linen monogram throw** | Initial or surname | **[Etsy]** 2026 color and texture |

**Peaks:** Q4 (list now) and **Mother's Day**, so list B1–B3 by early April.

**Listing photos:** draped over a sofa arm (hero); a close-up of the sherpa texture; a person holding it to show scale; a personalization example; and the gift moment of someone opening it.

---

## 6. Build once, sell four ways

The biggest efficiency gain is to **draw one illustration library and use it across all four product lines**:

| Shared asset | Wall art | Ornament | Desk mat | Blanket |
|---|---|---|---|---|
| Felted / stitched animal set (8–12 animals) | W1, W2, W3 | O6 | — | B5 |
| Dog and cat breed line-art library (40–60 breeds) | W7 | O7, O8 | — | B3 |
| Original fantasy world map | W10 | — | D4 | — |
| Dark botanical / celestial set | W9 | O10 | D1, D2 | — |
| Birth-month flower set (12 flowers) | Grandma garden print | O9 variant | — | B1 |
| Patina Blue / washed-linen textures | W4, W13 | — | D8 | B6 |
| House illustrations (6 styles) | W5 variant | O4 | — | — |

Seven asset libraries produce more than 40 listings.

---

## 7. Launch schedule

**Week 1 (by October 20): ornaments.** Create O1, O2, O3, O4, O6, O7 and O8 in all three shapes, which makes 7 listings. Order one sample each of O1 and O2. Photograph them, and swap the photos into the live listings when the samples arrive.

**Week 2: Q4 blankets and desk mats.** List B1, B3 and B4, then D1, D2, D3 and D4.

**Weeks 2–3: wall art.** Draw the felted animal library first. Then list W1, W2, W3, W4, W5, W8, W9 and W13, each with unframed and framed variations.

**Week 4: remaining ornaments and wall art.** List O5, O9, O10 and O11, then W10, W11, W12 and W14.

**January:** list Valentine's versions (couple map W4, couple portrait W6 and heart ornament) and start Mother's Day blankets B1 and B2.

### Quality checklist (every file, before publishing)
- [ ] Spelling checked in every text layer, including test names with long values (for example, "Christopher", "Bartholomew-Smith").
- [ ] Safe zones respected (posters 0.5 in, ornament hole 0.3 in, desk mat 0.5 in, blanket 2 in).
- [ ] Resolution at or above spec for the largest size offered.
- [ ] Personalization layer names match the Etsy field names.
- [ ] Production partner set to "Printify" on the listing.
- [ ] No brands, franchises, celebrity images or trademarked phrases; fonts licensed for commercial use.
- [ ] Hero image readable at thumbnail size.

### Keyword seeds to validate in eRank or Marmalead
- **Wall art:** personalized nursery print, farm animal nursery decor, birth stats print, custom map print wedding, family name sign est, sage botanical print set, whimsigoth wall art, fantasy map poster, retro 70s wall art, Italian kitchen print, mahjong wall art.
- **Ornaments:** family name ornament 2026, first christmas married ornament 2026, new home ornament 2026, baby first christmas ornament 2026, dog ornament personalized, pet memorial ornament, embroidered ornament, Nonna ornament, Gothmas ornament.
- **Desk mats:** cottagecore desk mat, dark floral desk mat, celestial desk mat, whimsigoth desk mat, fantasy map desk mat, kawaii desk mat, desk mat dorm gift.
- **Blankets:** grandma blanket personalized, birth flower blanket grandma, pet memorial blanket, family photo blanket, personalized baby blanket.

---

## Sources

- Wall art: [EtsyHunt best-selling wall art 2026](https://etsyhunt.com/best-etsy-wall-art) · [EtsyHunt posters](https://etsyhunt.com/best-etsy-posters) · [Merchize wall art trends 2026](https://merchize.com/wall-art-trends/) · [Insight Agent wall art](https://www.insightagent.app/trends/etsy-wall-art) · [Insight Agent printable wall art](https://www.insightagent.app/guides/best-selling-printable-wall-art-etsy) · [Accio](https://www.accio.com/business/best-selling-wall-art-on-etsy) · [Outfy home decor](https://www.outfy.com/blog/top-selling-etsy-home-decor-trends/) · [ResizeFlow wall art categories](https://resizeflow.com/blog/trending-etsy-wall-art-categories-2026) · [Gelato trending products](https://www.gelato.com/blog/trending-products-to-sell) · [Etsy: trending wall art 2026](https://www.etsy.com/market/trending_wall_art_in_2026)
- Ornaments: [Teeinblue 40 ornaments (2026)](https://teeinblue.com/blogs/en/christmas-ornaments-to-make-and-sell) · [Merchize top 35 Etsy ornaments 2026](https://merchize.com/best-etsy-christmas-ornaments/) · [EtsyHunt Christmas ornaments](https://etsyhunt.com/best-etsy-christmas-ornaments) · [Printway personalized Christmas gifts](https://printway.io/en/blogs/best-personalized-christmas-gifts-to-sell-on-etsy-and-amazon) · [Printify ceramic ornament guidelines](https://help.printify.com/hc/en-us/articles/4483628673681-What-are-the-design-guidelines-for-ceramic-ornaments) · [Printify ceramic ornaments 1/3/5/10](https://printify.com/app/products/1370/generic-brand/ceramic-ornaments-1pc-3pcs-5pcs-10pcs) · [Printify personalized ornaments](https://printify.com/personalized-christmas-ornaments/)
- Desk mats: [Etsy best seller desk mats](https://www.etsy.com/market/best_seller_desk_mats) · [Etsy top selling desk mat](https://www.etsy.com/market/top_selling_desk_mat) · [Printify custom desk mats](https://printify.com/custom-desk-mat/)
- Blankets: [RankHero "grandma blanket"](https://www.rankhero.com/keywords/grandma-blanket) · [ASInsight personalized photo blanket](https://www.asinsight.com/report/US/personalized-photo-blanket) · [Etsy photo collage blankets](https://www.etsy.com/market/personalized_blankets_photo_collage) · [EtsyHunt personalized baby blankets](https://etsyhunt.com/best-personalized-baby-blankets-etsy) · [Printify bedding](https://printify.com/app/products/home-and-living/bedding) · [Printify velveteen plush](https://printify.com/app/products/522/generic-brand/velveteen-plush-blanket) · [Printify sherpa fleece](https://printify.com/app/products/238/generic-brand/sherpa-fleece-blanket)
- Aesthetics: [Exploding Topics: whimsigoth](https://explodingtopics.com/topic/whimsigoth?period=120) · [RankHero whimsigoth decor](https://www.rankhero.com/keywords/whimsigoth-decor) · [RankHero light academia decor](https://www.rankhero.com/keywords/light-academia-decor) · [SellerApp Etsy trends](https://www.sellerapp.com/blog/etsy-trends/)
- Etsy official: [Seller Trend Report SS 2026](https://www.etsy.com/seller-handbook/article/1473931456647) · [2026 Color and Texture of the Year](https://www.etsy.com/news/etsy-announces-its-2026-color-of-the-year-a-plus-the-first-ever-texture-of-the-year) · [Holiday 2024 trend report](https://www.etsy.com/seller-handbook/article/1291219948731)
- Printify prices and files: [Posters category (framed $35.89, matte $4.96)](https://printify.com/app/products/home-and-living/posters) · [Framed vertical poster](https://printify.com/app/products/540/roma-imaging/framed-vertical-poster) · [RatioReady Printify specs](https://ratioready.com/print-ready/printify) · [FreePrintTools Printify image requirements](https://freeprinttools.com/blog/printify-image-requirements/) · [Let's Enhance DPI guide](https://letsenhance.io/blog/all/image-resolution-print-quality/)
- Listing photos: [Lovart Etsy listing images](https://www.lovart.ai/it/blog/03-cluster-etsy-listing-images) · [Dynamic Mockups](https://dynamicmockups.com/knowledge/how-to-create-etsy-mockups-no-photoshop/)
