---
name: web-design
description: Premium UI/UX design system — color psychology, typography, GSAP motion, conversion-first layouts. Full agency-grade output for any project.
---

# AGENCY-LEVEL PREMIUM UI/UX SKILL
**Version 2.0 | Beyond UI — Marketing, Psychology, Motion, Brand, Product**

> "Great interfaces are not built — they are orchestrated. Every pixel, word, motion, and color is a decision that either converts or repels a human being."

---

## MANDATORY READING ORDER
Before writing **one line of code**, read these files in order:
1. `COLOR_PSYCHOLOGY.md` — Human emotion mapping to color
2. `100_GRAPHIC_STYLES.md` — Pick the style
3. `TYPOGRAPHY_SYSTEM.md` — Font decisions
4. `GSAP_ANIMATIONS.md` — Motion system
5. `SCROLL_EFFECTS.md` — Scroll orchestration
6. `MARKETING_COPY.md` — Conversion thinking
7. `SITEMAP_LAYOUTS.md` — Structure thinking

---

## PHASE 0 — THE BRIEF INTERROGATION (Non-Negotiable)

Answer ALL before touching code. If unanswered, assume from context.

```
WHO    → Target persona (age, profession, device, emotional state on arrival)
WHAT   → Primary conversion goal (sign up / buy / trust / contact / consume)
WHY    → Why should they choose this (USP, differentiation)
FEEL   → 3 emotional adjectives the site must produce (e.g., "powerful, trusted, inspired")
STYLE  → Style number from 100_GRAPHIC_STYLES.md (1–100)
MOTION → Dominant animation from 100_ANIMATIONS.md (GSAP/Framer/Anime.js)
PALETTE→ From COLOR_PSYCHOLOGY.md — emotion-first color selection
ICONS  → Icon system (see ICON_SYSTEMS.md — Phosphor / Heroicons / Tabler / custom SVG)
BG     → Background treatment (image/texture/3D/gradient mesh/video)
COPY   → Tone (see MARKETING_COPY.md)
```

---

## PHASE 1 — ARCHITECTURE (Before Design)

### 1.1 Sitemap First
Every page serves ONE purpose. Consult `SITEMAP_LAYOUTS.md`:
```
HOME          → Awareness + First impression + Primary CTA
ABOUT         → Trust + Story + Team + Mission
SERVICES      → Value clarity + Positioning + Secondary CTA
WORK/PORTFOLIO→ Proof + Social proof + Case studies
PRICING       → Conversion + Objection handling + Urgency
CONTACT       → Friction removal + Multi-channel + Trust signals
BLOG/CONTENT  → SEO + Authority + Top-of-funnel
LANDING PAGE  → Single action, zero distraction
```

### 1.2 Page Anatomy (Every Page)
```
ABOVE THE FOLD:
  └── Nav (sticky, scroll-aware)
  └── Hero (primary message + CTA in < 6 words headline)
  └── Sub-headline (value prop, < 20 words)
  └── Social proof line (logos, numbers, reviews)
  └── Hero visual (image/animation/3D — never stock photos)

BODY:
  └── Problem → Agitation → Solution (PAS framework)
  └── Feature sections with alternating layouts
  └── Testimonials / Case studies
  └── FAQ section (objection handling)

BELOW FOLD:
  └── Secondary CTA
  └── Trust signals (certifications, guarantees, press)
  └── Footer
```

### 1.3 Layout Personality System
Choose ONE layout personality (see `SITEMAP_LAYOUTS.md`):
- **Editorial**: Large whitespace, serif display, magazine feel
- **Dashboard**: Dense, grid-heavy, data-centric
- **Campaign**: Full-bleed visuals, minimal text, big statements
- **Storytelling**: Scroll-driven narrative with GSAP triggers
- **Catalog**: Product-grid, filtereable, high-density
- **Immersive**: Three.js/WebGL, full-screen takeovers
- **Brutalist**: Grid-visible, raw, typographic-dominant
- **Luxury**: Slow, ceremonial, whitespace as premium signal

---

## PHASE 2 — DESIGN SYSTEM CONSTRUCTION

### 2.1 Color System (from COLOR_PSYCHOLOGY.md)
```css
/* ALWAYS define before anything else */
:root {
  /* Primary — the emotional anchor */
  --clr-primary-h: 262;          /* HSL hue value */
  --clr-primary-s: 83%;
  --clr-primary-l: 58%;
  --clr-primary: hsl(var(--clr-primary-h), var(--clr-primary-s), var(--clr-primary-l));
  
  /* Full shade scale — ALWAYS define all 11 */
  --clr-primary-50:  hsl(262, 83%, 97%);
  --clr-primary-100: hsl(262, 83%, 93%);
  --clr-primary-200: hsl(262, 83%, 86%);
  --clr-primary-300: hsl(262, 83%, 76%);
  --clr-primary-400: hsl(262, 83%, 66%);
  --clr-primary-500: hsl(262, 83%, 58%);  /* base */
  --clr-primary-600: hsl(262, 83%, 48%);
  --clr-primary-700: hsl(262, 83%, 40%);
  --clr-primary-800: hsl(262, 83%, 30%);
  --clr-primary-900: hsl(262, 83%, 18%);
  --clr-primary-950: hsl(262, 83%, 10%);
  
  /* Secondary — emotional counterpoint */
  /* Neutral — 11 shades */
  /* Semantic — success/warning/error/info */
  /* Surfaces — bg/surface-1/surface-2/surface-3 */
}
```

### 2.2 Typography System (from TYPOGRAPHY_SYSTEM.md)
```
ALWAYS define:
- Display font: Character/Personality (e.g., Playfair, Bebas, Fraunces, Clash)
- Body font: Readability (e.g., Satoshi, DM Sans, Plus Jakarta, Geist)
- Mono font: Code/technical (e.g., Space Mono, JetBrains, Berkeley Mono)
- Type scale: 8 levels minimum (xs → 9xl)
- Letter spacing: Tighten headings, loosen all-caps labels
- Line height: 1.1–1.2 display, 1.5–1.7 body
```

### 2.3 Spacing & Grid
```
Base unit: 4px
Scale: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96, 128, 160, 192, 256px
Grid: 12 columns, variable gutters (16px mobile → 32px desktop)
Container: max 1280px, with fluid padding clamp(16px, 4vw, 80px)
Section rhythm: Minimum 96px top/bottom padding
```

### 2.4 Motion Design Tokens
```javascript
// ALWAYS define before animating
const MOTION = {
  ease: {
    out:    [0.16, 1, 0.3, 1],      // fast start, slow settle
    spring: [0.34, 1.56, 0.64, 1], // slight overshoot
    smooth: [0.4, 0, 0.2, 1],      // material standard
    enter:  [0, 0, 0.2, 1],        // decelerate
    exit:   [0.4, 0, 1, 1],        // accelerate
  },
  duration: {
    instant: 100,
    fast:    200,
    base:    300,
    slow:    500,
    reveal:  700,
    scene:   1200,
    cinematic: 2000,
  },
  stagger: {
    tight:  30,
    normal: 80,
    loose:  150,
    dramatic: 250,
  }
}
```

---

## PHASE 3 — BACKGROUND & ATMOSPHERE

**Rule**: Flat solid backgrounds are forbidden on premium sites.

### 3.1 Background Hierarchy
```
TIER 1 — Immersive (most premium):
  - Three.js / WebGL shader backgrounds
  - Spline 3D scenes embedded via <iframe> or SDK
  - Video loop (muted, autoplay, 15–30s)
  - Lottie full-canvas animation

TIER 2 — Rich (premium):
  - Multi-layered gradient mesh (5+ radial gradients)
  - SVG noise + gradient hybrid
  - CSS aurora animation (shifting hues)
  - Subtle image with color overlay + grain
  - Glassmorphism layered over gradient

TIER 3 — Textured (standard premium):
  - Grain overlay on gradient
  - Dot/grid pattern on surface
  - Halftone pattern + color wash
  - SVG pattern tiles (see BACKGROUND_ASSETS.md)
```

### 3.2 Background Images
Always use **Agency-grade** imagery (Unsplash/Pexels) optimized for the mood.
**Standard**: Refer to `PREMIUM_IMAGERY.md` for URL templates and mapping.

#### The SV "Veneer" Rule:
Never use a stock photo raw. Always apply a CSS brand overlay (Phase 3.4):
```html
<style>
.hero {
  background-image:
    linear-gradient(to bottom, rgba(0,0,0,0.8), rgba(0,0,0,0.4)),
    url('https://images.unsplash.com/featured/?premium,minimalist,architecture');
  background-size: cover;
}
</style>
```

### 3.3 Grain Texture (Universal Premium Signal)
```css
/* Add to any section that needs premium texture */
.grain-overlay {
  position: relative;
}
.grain-overlay::after {
  content: '';
  position: absolute;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)' opacity='0.05'/%3E%3C/svg%3E");
  pointer-events: none;
  border-radius: inherit;
}
```

---

## PHASE 4 — ICON SYSTEMS (See ICON_SYSTEMS.md)

**NEVER use Lucide React as primary icons on premium sites.**

### Approved Premium Icon Systems:
```
1. Phosphor Icons    → phosphoricons.com  — 9 weights, 1300+ icons
   npm install @phosphor-icons/react
   
2. Heroicons         → heroicons.com     — Tailwind-adjacent, clean
   npm install @heroicons/react
   
3. Tabler Icons      → tabler-icons.io   — 5000+ outlined icons
   npm install @tabler-icons/react
   
4. Remix Icon        → remixicon.com     — 2800+ dual-tone
   
5. Feather Icons     → feathericons.com  — Ultra minimal
   npm install feather-icons

6. Custom SVG        → Best for brand-specific icons
   — Draw in Figma, export as optimized SVG
   — Inline for animation capability
   — Use currentColor for theme flexibility

7. Lordicon          → lordicon.com      — Animated Lottie icons
   <script src="https://cdn.lordicon.com/lordicon.js"></script>
   <lord-icon src="..." trigger="hover"></lord-icon>
```

---

## PHASE 5 — ANIMATION ORCHESTRATION

### 5.1 Animation Library Selection
```
GSAP + ScrollTrigger  → Industry standard, most powerful
  Best for: Complex scroll narratives, SVG morphing, timeline sequences
  CDN: https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js
  
Framer Motion         → React-first, declarative
  Best for: React components, gesture-driven, layout animations
  npm install framer-motion
  
Anime.js              → Lightweight, CSS properties + SVG
  Best for: Staggered lists, morphing paths, property animation
  CDN: https://cdnjs.cloudflare.com/ajax/libs/animejs/3.2.1/anime.min.js
  
Lenis                 → Smooth scroll (replace native scroll)
  npm install @studio-freight/lenis
  CDN: https://cdn.jsdelivr.net/gh/studio-freight/lenis@1.0.42/bundled/lenis.min.js
  
Splitting.js          → Text splitting for char/word animations
  CDN: https://unpkg.com/splitting/dist/splitting.min.js
```

### 5.2 GSAP Initialization Template
```javascript
// ALWAYS initialize in this order
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { TextPlugin } from 'gsap/TextPlugin';
import { MorphSVGPlugin } from 'gsap/MorphSVGPlugin';
import Lenis from '@studio-freight/lenis';

gsap.registerPlugin(ScrollTrigger, TextPlugin, MorphSVGPlugin);

// Smooth scroll setup
const lenis = new Lenis({ duration: 1.2, easing: t => Math.min(1, 1.001 - Math.pow(2, -10 * t)) });
function raf(time) { lenis.raf(time); requestAnimationFrame(raf); }
requestAnimationFrame(raf);
// Connect Lenis to ScrollTrigger
lenis.on('scroll', ScrollTrigger.update);
gsap.ticker.add(time => lenis.raf(time * 1000));
gsap.ticker.lagSmoothing(0);
```

### 5.3 Scroll Narrative Architecture
See full patterns in `GSAP_ANIMATIONS.md`. Key principle:
```
SCROLL ACTS:
  Act 1 (0–20% scroll):   Hero reveal, text scramble, logo entrance
  Act 2 (20–40% scroll):  Feature pinning, counter animation, image reveal
  Act 3 (40–60% scroll):  Horizontal scroll section OR sticky panels
  Act 4 (60–80% scroll):  Testimonials, social proof cascade
  Act 5 (80–100% scroll): CTA section, footer entrance
```

---

## PHASE 6 — MARKETING LAYER (See MARKETING_COPY.md)

Premium design without marketing thinking = beautiful but unconverting.

### 6.1 Conversion Architecture
```
ATTENTION    → Hero headline captures in < 3 seconds
INTEREST     → Sub-headline clarifies the value
DESIRE       → Features show transformation (before → after)
ACTION       → CTA is specific, urgent, low-friction
TRUST        → Social proof near every CTA
```

### 6.2 Headline Formula
```
[RESULT] without [PAIN] — for [PERSONA]
Example: "Ship premium interfaces without the 6-figure agency bill — for indie developers"

OR: [NUMBER] + [THING] that [BENEFIT]
Example: "100 design styles that make your LLM produce awwwards-level UI"
```

### 6.3 CTA Copy Rules
```
❌ "Submit", "Click Here", "Learn More", "Get Started" (too generic)
✅ Specific + value-forward:
   "Download the Skill (Free)"
   "See Live Demo →"
   "Start Building Premium UI"
   "Get 100 Styles Now"
```

---

## PHASE 7 — THE PREMIUM QUALITY GATE

### Must-Pass Before Delivery:
```
TYPOGRAPHY
□ Display font is character-rich (not Inter/Roboto/Arial)
□ Type hierarchy has 3+ distinct levels
□ Letter-spacing: negative on headlines, positive on labels
□ Max line length 65ch for body copy

COLOR  
□ All colors defined as CSS custom properties
□ Emotion verified against COLOR_PSYCHOLOGY.md
□ 4.5:1 contrast minimum met
□ Tinted shadows (not pure black)
□ Background has depth (not flat solid)

MOTION
□ GSAP / Anime.js / Framer Motion in use (not just CSS)
□ Lenis smooth scroll active
□ Page load stagger present
□ ScrollTrigger reveals on all sections
□ Hover states on every interactive element
□ One signature "wow" animation per page

ICONS
□ Premium icon library (not Lucide alone)
□ Consistent weight/style across all icons
□ Animated icons where contextually appropriate (Lordicon)

IMAGES/BG
□ Background has texture/depth/imagery
□ No flat solid color hero
□ Images have color overlay for brand consistency
□ Grain texture applied where appropriate

MARKETING
□ Headline follows conversion formula
□ CTA copy is specific, not generic
□ Social proof visible above the fold
□ FAQ or objection-handling section present

PERFORMANCE
□ Google Fonts with font-display: swap
□ Images with loading="lazy" below fold
□ GSAP animations use will-change: transform
□ No layout shift from font loading (font-size-adjust)

ACCESSIBILITY
□ WCAG AA contrast (4.5:1 body, 3:1 large)
□ Focus-visible styles
□ Semantic HTML
□ prefers-reduced-motion respected
□ Alt text on all images
```

---

## SLASH COMMANDS
See `SLASH_COMMANDS.md` for full reference.

Quick reference:
```
/design [style-number]    → Apply style from 100_GRAPHIC_STYLES.md
/animate [type]           → Apply animation from 100_ANIMATIONS.md
/scroll [effect]          → Apply scroll effect
/palette [emotion]        → Generate palette from COLOR_PSYCHOLOGY.md
/component [name]         → Generate premium component
/page [type]              → Generate full page layout
/hero [style]             → Generate hero section variant
/evaluate                 → Run quality rubric on current design
/marketing                → Apply conversion layer
/agent [task]             → Spawn sub-agent from AGENT.md
```

---

## SUB-AGENTS
See `AGENT.md` for full orchestration tree.

Key agents:
- `@visual-director`   → Style, palette, typography decisions
- `@motion-engineer`   → GSAP/Framer/Anime.js implementation
- `@copy-strategist`   → Marketing copy, headlines, CTAs
- `@scroll-architect`  → ScrollTrigger narrative sequencing
- `@component-builder` → Premium component production
- `@quality-auditor`   → Runs full evaluation rubric
