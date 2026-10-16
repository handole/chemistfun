# ✍️ TYPOGRAPHY SYSTEM — PREMIUM FONT PAIRINGS

## THE GOLDEN RULE
**Display font = the personality. Body font = the readability. They must DISAGREE slightly — contrast creates interest.**

---

## PREMIUM FONT PAIRINGS (20 curated combinations)

| # | Display Font | Body Font | Personality | Best For |
|---|-------------|-----------|-------------|----------|
| 1 | Playfair Display | DM Sans | Editorial luxury | Fashion, magazine, editorial |
| 2 | Fraunces | Satoshi | Organic intelligence | AI, creative, organic SaaS |
| 3 | Cormorant Garamond | Jost | Classical refined | Luxury, wine, architecture |
| 4 | Bebas Neue | IBM Plex Sans | Bold constructivist | Agency, sport, media |
| 5 | Space Mono | Geist | Hacker-minimal | Dev tools, CLI, crypto |
| 6 | Clash Display | Plus Jakarta Sans | Modern assertive | Startup, SaaS, B2B |
| 7 | Syne | DM Mono | Experimental editorial | Design studio, art |
| 8 | Cabinet Grotesk | Manrope | Confident premium | E-commerce, consumer |
| 9 | Libre Baskerville | Nunito Sans | Trustworthy classic | Finance, legal, healthcare |
| 10 | Neue Haas Grotesk | Same lighter weight | Pristine Swiss | Enterprise, corporate |
| 11 | Cinzel | EB Garamond | Timeless ceremonial | Wedding, theater, events |
| 12 | Unbounded | Noto Sans | Heavy future | Crypto, Web3, gaming |
| 13 | Abril Fatface | Lato | Friendly impact | Food, lifestyle, consumer |
| 14 | Marcellus | Raleway | Elegant simplicity | Spa, wellness, hotel |
| 15 | Anton | Open Sans | High-impact mass | News, headlines, editorial |
| 16 | Orbitron | Share Tech Mono | Sci-fi technical | Tech, gaming, future |
| 17 | Lobster | Quicksand | Friendly retro | Restaurant, café, lifestyle |
| 18 | Rozha One | Mulish | Heritage bold | Cultural, traditional |
| 19 | Big Shoulders Display | Inter | Industrial clarity | Manufacturing, logistics |
| 20 | Fraunces | General Sans | Warmly modern | General premium default |

---

## TYPE SCALE (CSS Variables)

```css
:root {
  /* Modular scale: 1.333× (perfect fourth) */
  --text-xs:   0.563rem;   /*  9px */
  --text-sm:   0.75rem;    /* 12px */
  --text-base: 1rem;       /* 16px */
  --text-md:   1.125rem;   /* 18px */
  --text-lg:   1.333rem;   /* 21px */
  --text-xl:   1.5rem;     /* 24px */
  --text-2xl:  2rem;       /* 32px */
  --text-3xl:  2.666rem;   /* 42px */
  --text-4xl:  3.552rem;   /* 57px */
  --text-5xl:  4.736rem;   /* 76px */
  --text-6xl:  6.315rem;   /* 101px */
  --text-7xl:  8.42rem;    /* 135px */
  --text-8xl:  11.22rem;   /* 179px */
  --text-9xl:  14.96rem;   /* 239px */
  
  /* Line heights */
  --leading-tight:   1.05;
  --leading-snug:    1.2;
  --leading-normal:  1.5;
  --leading-relaxed: 1.7;
  --leading-loose:   2;
  
  /* Letter spacing */
  --tracking-tightest: -0.06em;
  --tracking-tight:    -0.03em;
  --tracking-normal:   0em;
  --tracking-wide:     0.05em;
  --tracking-wider:    0.1em;
  --tracking-widest:   0.2em;
}
```

---

# 🔧 ICON SYSTEMS — PREMIUM IMPLEMENTATION

## PRIMARY SYSTEMS

### 1. Phosphor Icons ⭐ (Recommended for premium dark sites)
```jsx
// npm install @phosphor-icons/react
import { ArrowRight, Star, Check, Lightning, Brain } from '@phosphor-icons/react';

// Weights: thin, light, regular, bold, fill, duotone
<ArrowRight size={20} weight="duotone" color="var(--clr-primary)" />

// Duotone pattern (2-color icons)
<Brain size={32} weight="duotone" 
  style={{'--phosphor-second-opacity': '0.3'}} 
  color="var(--clr-primary)" />
```

### 2. Heroicons (Tailwind ecosystem)
```jsx
// npm install @heroicons/react
import { ArrowRightIcon, CheckIcon } from '@heroicons/react/24/outline'
import { StarIcon } from '@heroicons/react/24/solid'
<ArrowRightIcon className="w-5 h-5 text-primary" />
```

### 3. Tabler Icons (5000+ options)
```jsx
// npm install @tabler-icons/react
import { IconArrowRight, IconBrain } from '@tabler-icons/react'
<IconBrain size={24} stroke={1.5} color="var(--clr-primary)" />
```

### 4. Lordicon — Animated Icons (Premium Differentiator)
```html
<!-- Add to <head> -->
<script src="https://cdn.lordicon.com/lordicon.js"></script>

<!-- Usage -->
<lord-icon
  src="https://cdn.lordicon.com/lupuorrc.json"
  trigger="hover"
  colors="primary:#7C3AED,secondary:#00D9B8"
  style="width:48px;height:48px">
</lord-icon>

<!-- Free animated icons: https://lordicon.com/icons -->
<!-- Popular IDs:
  lupuorrc → Star/award
  kbtmbyzy → Rocket
  jdgfsfzr → Lightning/bolt  
  bdnxnero → Brain/AI
  wjyqkiew → Arrow right
  hpivxauj → Check/success
-->
```

### 5. Custom SVG Icons (Best for brand-specific)
```html
<!-- Template for custom icon -->
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
  <path d="..." stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
</svg>

<!-- Use currentColor for theme flexibility -->
<style>
.icon { color: var(--clr-primary); }
.icon:hover { color: var(--clr-secondary); transition: color 0.2s; }
</style>
```

---

## ICON USAGE RULES

```
Size hierarchy:
  Navigation: 20-24px
  Feature cards: 28-36px (with colored container)
  Hero/large: 40-56px
  Decorative: 80-120px (very light opacity)

Container styles for feature icons:
```
```css
/* Glowing icon container */
.icon-container {
  width: 56px; height: 56px;
  border-radius: 14px;
  background: rgba(var(--clr-primary-rgb), 0.12);
  border: 1px solid rgba(var(--clr-primary-rgb), 0.2);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 0 20px rgba(var(--clr-primary-rgb), 0.15);
  transition: all 0.3s ease;
}
.icon-container:hover {
  background: rgba(var(--clr-primary-rgb), 0.2);
  box-shadow: 0 0 40px rgba(var(--clr-primary-rgb), 0.25);
  transform: translateY(-2px);
}
```
