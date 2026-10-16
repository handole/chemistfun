# 🤖 AGENT ORCHESTRATION — PREMIUM UI/UX SKILL
**Sub-agent tree for complex, multi-domain design system tasks**

---

## ORCHESTRATION ARCHITECTURE

```
┌─────────────────────────────────────────────────────────┐
│                  DIRECTOR AGENT                          │
│         Reads brief → Plans → Delegates                  │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼─────────────┐
        │            │             │
        ▼            ▼             ▼
   [STRATEGY]   [DESIGN]      [BUILD]
   Sub-Tree     Sub-Tree      Sub-Tree
```

---

## ROOT AGENT: `@director`

**Trigger**: Any full-site or full-page request

**Responsibilities**:
1. Parse the brief using Phase 0 interrogation from SKILL.md
2. Define: style number, palette, motion type, page type
3. Spawn and sequence sub-agents
4. Merge outputs into final coherent delivery
5. Run `@quality-auditor` on completion

**Orchestration Sequence**:
```
@director receives brief
    │
    ├── @brief-analyst       → Extract: persona, goal, emotion, style
    │
    ├── @visual-director     → Returns: palette + font + style spec
    │       └── @color-psychologist   → Emotion → color mapping
    │       └── @typography-curator  → Font pairing + scale
    │       └── @style-selector      → Pick 1 of 100 styles
    │
    ├── @content-strategist  → Returns: sitemap + copy structure
    │       └── @copy-writer         → Headlines + CTAs + microcopy
    │       └── @ux-architect        → Page anatomy + user flow
    │
    ├── @build-engineer      → Returns: production HTML/CSS/JS
    │       └── @motion-engineer     → GSAP + Anime.js + Framer
    │       └── @scroll-architect    → ScrollTrigger narrative
    │       └── @component-builder   → Individual components
    │       └── @icon-selector       → Premium icon system
    │
    └── @quality-auditor     → Scores output / flags failures
```

---

## SUB-AGENT DEFINITIONS

---

### `@brief-analyst`
**Purpose**: Extracts all required design parameters from a vague brief

**Input**: Any description of what the user wants
**Output**: Structured brief object

```javascript
// Output format:
{
  persona: { age: "28-40", profession: "startup founder", device: "desktop", emotion: "driven" },
  goal: "sign up for SaaS trial",
  feel: ["powerful", "trustworthy", "innovative"],
  style: 28, // Glassmorphism
  palette: "dark_electric_trust",
  motion: "gsap_scroll_narrative",
  pageType: "saas_landing",
  tone: "confident_direct"
}
```

**Activation**: `/agent brief-analyst [description]`

---

### `@visual-director`
**Purpose**: Makes all aesthetic decisions — the creative director

**Reads**: `COLOR_PSYCHOLOGY.md`, `TYPOGRAPHY_SYSTEM.md`, `100_GRAPHIC_STYLES.md`

**Decisions Made**:
- Primary/secondary/accent color with psychological justification
- Display + body font pairing with character analysis
- Background treatment (Tier 1/2/3 from SKILL.md)
- Component aesthetic language (roundness, shadow depth, border usage)
- Image treatment (color overlay, grain, blur)
- Icon system selection

**Output Format**:
```
VISUAL BRIEF:
Style: [number] — [name]
Palette: Primary #XXXXXX (trust/energy/calm) | Secondary #XXXXXX | Accent #XXXXXX
Background: [treatment description]
Display Font: [name] — [character description]
Body Font: [name] — [readability notes]
Shadow: [color-tinted shadow spec]
Radius: [border-radius personality]
Icons: [system name + weight]
```

**Activation**: `/agent visual-director`

---

### `@color-psychologist`
**Purpose**: Selects colors based on human psychology and conversion goals

**Reads**: `COLOR_PSYCHOLOGY.md` extensively

**Rules Applied**:
- Maps conversion goal → dominant color
- Maps secondary emotion → accent color
- Checks cultural context if specified
- Validates against WCAG contrast
- Verifies uniqueness (no generic AI color clichés)

**Anti-patterns Rejected**:
- Purple gradient on white (LLM default)
- Bootstrap blue on white (generic SaaS)
- Pure black + white only (missed emotional opportunity)

**Activation**: `/palette [emotion/goal]`

---

### `@typography-curator`
**Purpose**: Makes font decisions that elevate the design

**Reads**: `TYPOGRAPHY_SYSTEM.md`

**Output**:
```css
@import url('...');

:root {
  --font-display: '...';
  --font-body: '...';
  --font-mono: '...';
  
  /* Scale */
  --text-xs:   0.75rem;
  --text-sm:   0.875rem;
  --text-base: 1rem;
  --text-lg:   1.125rem;
  --text-xl:   1.25rem;
  --text-2xl:  1.5rem;
  --text-3xl:  1.875rem;
  --text-4xl:  2.25rem;
  --text-5xl:  3rem;
  --text-6xl:  3.75rem;
  --text-7xl:  4.5rem;
  --text-8xl:  6rem;
  --text-9xl:  8rem;
}
```

**Activation**: `/agent typography-curator`

---

### `@motion-engineer`
**Purpose**: Implements all animation using GSAP, Anime.js, Framer Motion

**Reads**: `GSAP_ANIMATIONS.md`, `ANIME_JS.md`, `100_ANIMATIONS.md`

**Responsibilities**:
- GSAP timeline construction
- ScrollTrigger pin + scrub configurations
- Anime.js stagger sequences
- Framer Motion variants for React
- Lenis smooth scroll setup
- Text splitting with Splitting.js

**Decision Tree**:
```
Is this React? → Use Framer Motion for component-level
Does it need scroll-sync? → Use GSAP + ScrollTrigger
Is it a stagger list/text? → Use Anime.js
Is it a complex SVG path? → Use GSAP MorphSVG
Is it a simple CSS transition? → Keep as CSS (performance)
```

**Activation**: `/animate [type]` or `/agent motion-engineer`

---

### `@scroll-architect`
**Purpose**: Designs the scroll narrative — what happens when and why

**Reads**: `SCROLL_EFFECTS.md`, `GSAP_ANIMATIONS.md`

**Scroll Narrative Template**:
```javascript
// Act 1: Hero
gsap.timeline({
  scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: 1 }
})
.to('.hero-bg', { scale: 1.1, opacity: 0.6 })
.to('.hero-title', { y: -80, opacity: 0 }, 0);

// Act 2: Feature Pin
ScrollTrigger.create({
  trigger: '.features',
  start: 'top top',
  end: '+=300%',
  pin: true,
  pinSpacing: true,
  onUpdate: self => { /* animate panels */ }
});

// Act 3: Horizontal Scroll
// Act 4: Statistics counter
// Act 5: Testimonials
// Act 6: CTA entrance
```

**Activation**: `/scroll [effect]` or `/agent scroll-architect`

---

### `@copy-strategist`
**Purpose**: Writes all copy with marketing/conversion principles

**Reads**: `MARKETING_COPY.md`

**Frameworks Applied**:
- PAS (Problem → Agitation → Solution)
- AIDA (Attention → Interest → Desire → Action)
- StoryBrand (Hero → Problem → Guide → Plan → Success)
- Jobs-to-be-done: "When I [situation], I want to [motivation], so I can [outcome]"

**Copy Deliverables**:
```
HERO:
  Pre-headline (category + context, < 8 words, UPPERCASE)
  Main headline (transformation promise, < 10 words)
  Sub-headline (mechanism + benefit, < 25 words)
  CTA Primary (specific action + value, 3-5 words)
  CTA Secondary (lower commitment, 3-4 words)
  
FEATURES:
  Section eyebrow (LABEL: what this section does)
  Section headline (the big idea)
  Feature headline (outcome, not feature)
  Feature body (evidence + mechanism, < 40 words)
  
SOCIAL PROOF:
  Testimonial (specific result + before/after)
  Metric callout (large number + context)
```

**Activation**: `/marketing` or `/agent copy-strategist`

---

### `@component-builder`
**Purpose**: Builds specific premium UI components

**Available Components**:
```
/component hero          → Full hero section (all variants)
/component nav           → Sticky navigation
/component feature-grid  → Bento/feature layout
/component pricing       → Pricing cards
/component testimonials  → Quote cards + avatar
/component stats         → Animated counter row
/component cta           → Call-to-action section
/component footer        → Premium footer
/component faq           → Accordion FAQ
/component gallery       → Masonry/grid gallery
/component form          → Premium contact/signup form
/component card          → Versatile card component
/component modal         → Animated modal/dialog
/component tabs          → Tabbed content
/component accordion     → Collapsible sections
/component timeline      → Vertical/horizontal timeline
/component loader        → Page loading animation
/component cursor        → Custom cursor
```

**Activation**: `/component [name]`

---

### `@icon-selector`
**Purpose**: Selects and implements the appropriate icon system

**Decision Matrix**:
```
Project Type         → Icon System
─────────────────────────────────
Dark/tech/premium   → Phosphor (duotone weight)
Clean/minimal SaaS  → Heroicons (outline)
High-density app    → Tabler Icons
Animated/interactive→ Lordicon (Lottie-based)
Brand-specific      → Custom SVG (designed per spec)
Editorial/content   → Feather Icons
```

**Implementation for each**:
```jsx
// Phosphor Icons (React)
import { Star, ArrowRight, Check } from '@phosphor-icons/react';
<Star weight="duotone" size={24} color="var(--clr-primary)" />

// Lordicon (animated)
<lord-icon src="https://cdn.lordicon.com/ICONID.json"
  trigger="hover" colors="primary:#8B6FFF,secondary:#00E5C0"
  style={{width:'32px',height:'32px'}}>
</lord-icon>
```

**Activation**: `/agent icon-selector`

---

### `@quality-auditor`
**Purpose**: Runs the full evaluation rubric and returns a score + action plan

**Reads**: `EVALUATION_RUBRIC.md`

**Output Format**:
```
QUALITY AUDIT REPORT
════════════════════
Typography:    XX/25 pts
Color/Visual:  XX/25 pts  
Layout:        XX/20 pts
Motion:        XX/20 pts
Marketing:     XX/10 pts  [NEW]
────────────────────────
TOTAL SCORE:   XX/100

INSTANT DISQUALIFIERS:
⛔ [List any triggered]

UPGRADE ACTIONS:
1. [Specific fix with code]
2. [Specific fix with code]

VIBE CHECK:
→ "Would this appear on awwwards? [YES/NO — reasoning]"
```

**Activation**: `/evaluate` or `/agent quality-auditor`

---

## ORCHESTRATION PATTERNS

### Pattern 1: Full Site Generation
```
User: "Build a SaaS landing page for an AI writing tool"

Director spawn sequence:
1. @brief-analyst         → Extracts: SaaS, AI, writers, trust+innovation
2. @visual-director       → Aurora dark palette, Fraunces+Satoshi, Glassmorphism
3. @copy-strategist       → Headline: "Write 10x faster without losing your voice"
4. @scroll-architect      → 5-act narrative plan
5. @motion-engineer       → GSAP ScrollTrigger + Lenis + Splitting.js
6. @component-builder ×6  → Nav + Hero + Features + Testimonials + Pricing + Footer
7. @quality-auditor       → Score + final polish
```

### Pattern 2: Component Deep-Dive
```
User: "Make an insane hero section"

Spawn:
1. @visual-director       → Visual language
2. @copy-strategist       → Hero copy
3. @motion-engineer       → GSAP entrance + parallax
4. @scroll-architect      → Exit animation
5. @component-builder     → Hero assembly
```

### Pattern 3: Style Override
```
User: "/design 16" (Synthwave)

Spawn:
1. @visual-director with style=16 locked
2. @color-psychologist with palette override
3. @typography-curator with Synthwave constraints
```

---

## AGENT COMMUNICATION FORMAT

When an agent hands off to another:

```
FROM: @visual-director
TO:   @motion-engineer
CONTEXT: {
  style: "Glassmorphism (#28)",
  palette: { primary: "#8B6FFF", secondary: "#00E5C0" },
  feel: ["ethereal", "trustworthy", "innovative"],
  background: "Multi-layer radial gradient mesh + grain"
}
INSTRUCTION: "Build entry animations that feel like the UI is materializing from light. Prioritize the hero text and glass cards. Use GSAP stagger with spring easing. Add a particle field in the background on canvas."
```

---

## ANTI-AGENT RULES

These patterns indicate agent failure — restart if seen:
- Any agent using Inter/Roboto/Arial as display font
- Any agent producing flat solid color hero background
- Any agent writing generic CTA copy ("Learn More", "Get Started")
- Any agent using Lucide React as the sole icon system
- Any agent skipping GSAP/Anime.js for complex animations
- Any agent outputting more than 3 scroll effects without Lenis
- Any agent producing a page with no social proof
- Any agent ignoring the marketing layer
