# 📣 MARKETING COPY & CONVERSION STRATEGY
**Premium design without marketing thinking = beautiful but unconverting**

---

## CONVERSION HIERARCHY

```
1. STOP THE SCROLL     → Headline + Visual that demands attention
2. MAKE THEM CARE      → Sub-headline that speaks to their desire
3. BUILD DESIRE        → Features framed as transformations
4. ELIMINATE DOUBT     → Social proof + trust signals
5. DEMAND ACTION       → Specific CTA with urgency/value
```

---

## HEADLINE FORMULAS

### Formula 1: Transformation Promise
`[New State] without [Current Pain]`
- "Ship premium UI without a 6-figure design agency"
- "Build trust instantly without years of reputation"
- "Look enterprise without enterprise pricing"

### Formula 2: Number + Benefit  
`[N] [Things] that [Result]`
- "100 design styles that make AI produce awwwards-level interfaces"
- "15 animations that make users stop scrolling"
- "One skill that replaces 17 design books"

### Formula 3: Direct Desire
`The [adjective] way to [verb] [result]`
- "The fastest way to build premium interfaces"
- "The smartest way to brief an AI designer"
- "The only design skill you'll ever need"

### Formula 4: Call Out the Persona
`For [persona] who [situation]`
- "For developers who hate shipping ugly software"
- "For founders who want design that converts"

---

## CTA COPY RULES

```
❌ FORBIDDEN CTAs:
"Submit", "Click Here", "Learn More", "Get Started", "Sign Up"

✅ PREMIUM CTAs (Specific + Value):
"Download the Skill (Free)"
"See It In Action →"
"Start Building Premium UI"
"Get All 100 Styles"
"Watch the Live Demo"
"Copy the Code"
"Ship Your First Premium Page"
"Join 50,000 Designers"
```

---

## SOCIAL PROOF PLACEMENT
```
Above fold:   Logo strip (logos of recognizable companies)
Near CTA:     Review stars + quote snippet
Feature area: Specific testimonial with result
Pricing:      "X companies this month" urgency
Footer:       Review platform badges
```

---

## FAQ = OBJECTION HANDLING

Every FAQ question is actually a sales objection:
```
"Is this for beginners?" → Addresses expertise anxiety
"How long does it take?" → Addresses time investment fear  
"Does this work with [tool]?" → Addresses compatibility doubt
"What if it doesn't work?" → Risk reversal
"Why should I trust this?" → Credibility question
```

---

# 🗺️ SITEMAP & LAYOUT SYSTEM

## PAGE ARCHITECTURE PATTERNS

### SaaS Landing Page
```
NAV (sticky, transparent → solid on scroll)
│
HERO (headline + sub + CTA + social proof)
│
LOGO STRIP (trusted by)
│
PROBLEM STATEMENT (PAS: Problem → Agitation)
│
SOLUTION / FEATURES (3-6 key features, alternating layout)
│
HOW IT WORKS (numbered steps, simple)
│
TESTIMONIALS (3+ specific, result-based)
│
PRICING (3 tiers, middle highlighted)
│
FAQ (5-7 objection-handling questions)
│
FINAL CTA (repeated, with urgency)
│
FOOTER
```

### Agency / Portfolio
```
NAV (minimal, logo + contact only)
│
HERO (bold statement + reel/showreel)
│
SELECTED WORK (grid, 4-6 case studies)
│
ABOUT (team + culture + values)
│
SERVICES (what you do, not how)
│
PROCESS (numbered, reassuring)
│
TESTIMONIALS
│
CONTACT CTA
│
FOOTER
```

### Product / E-commerce
```
NAV (logo + categories + search + cart)
│
HERO (seasonal campaign, one product)
│
FEATURED PRODUCTS (grid, 3-4)
│
CATEGORY NAVIGATION
│
BESTSELLERS / TRENDING
│
BRAND STORY (one paragraph)
│
REVIEWS / SOCIAL PROOF
│
NEWSLETTER SIGNUP
│
FOOTER
```

---

## LAYOUT SECTION PATTERNS

### Alternating Feature Layout (L/R swap)
```html
<section class="feature">
  <div class="feature-visual"><!-- image/animation left --></div>
  <div class="feature-copy"><!-- text right --></div>
</section>
<section class="feature reverse">
  <div class="feature-visual"><!-- image/animation right --></div>
  <div class="feature-copy"><!-- text left --></div>
</section>
```
```css
.feature { display: grid; grid-template-columns: 1fr 1fr; gap: 80px; align-items: center; padding: 80px 0; }
.feature.reverse { direction: rtl; }
.feature.reverse > * { direction: ltr; }
```

### Bento Grid (Mixed sizes)
```css
.bento {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: repeat(3, 240px);
  gap: 16px;
}
.bento-1x1 { grid-column: span 1; }
.bento-2x1 { grid-column: span 2; }
.bento-1x2 { grid-row: span 2; }
.bento-2x2 { grid-column: span 2; grid-row: span 2; }
.bento-3x1 { grid-column: span 3; }
.bento-4x1 { grid-column: span 4; }
```

### Sticky Scroll Sections
```css
.sticky-container { height: 400vh; } /* 4x viewport */
.sticky-inner {
  position: sticky;
  top: 0;
  height: 100vh;
  overflow: hidden;
}
```

### Full-Bleed Sections
```css
.full-bleed {
  width: 100vw;
  margin-left: calc(-50vw + 50%);
  padding: 80px max(48px, calc((100vw - 1280px) / 2));
}
```
