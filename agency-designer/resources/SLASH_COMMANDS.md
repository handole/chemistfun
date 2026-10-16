# ⚡ SLASH COMMANDS REFERENCE
**Complete list of commands for the Premium UI/UX Skill**

---

## USAGE SYNTAX
```
/command [required-arg] (optional-arg) —option
```
Use slash commands at the START of a prompt to activate a specific mode.

---

## 🎨 DESIGN COMMANDS

### `/design [style-number]`
Apply a specific style from 100_GRAPHIC_STYLES.md
```
/design 1       → Swiss / International Style
/design 15      → Vaporwave
/design 28      → Glassmorphism
/design 29      → Cybercore
/design 30      → Aurora
/design 40      → Japandi
/design 23      → Brutalism
```
**Output**: Full design spec (palette, fonts, CSS variables, component language)

---

### `/palette [emotion or goal]`
Generate a full color system from COLOR_PSYCHOLOGY.md
```
/palette trust         → Blues, navy, clean whites
/palette luxury        → Deep jewel tones, gold, black
/palette energy        → Warm oranges, reds, electric yellow  
/palette calm          → Soft sage, muted blues, cream
/palette innovation    → Electric purple, cyan, near-black
/palette nature        → Forest green, terracotta, sand
/palette urgency       → High-saturation red, bold black
/palette playful       → Rainbow brights, rounded everything
/palette dark-premium  → Deep surfaces, neon accents, grain
/palette editorial     → Black, white, one bold accent
```
**Output**: Full :root color system with 11-shade scales

---

### `/font [personality]`
Select a font pairing from TYPOGRAPHY_SYSTEM.md
```
/font editorial    → Playfair Display + DM Sans
/font tech         → Space Mono + Geist
/font luxury       → Cormorant + Plus Jakarta Sans
/font bold         → Bebas Neue + IBM Plex Sans
/font organic      → Fraunces + Satoshi
/font minimal      → Clash Display + Inter (body only exception)
/font humanist     → Libre Baskerville + Nunito Sans
/font experimental → Cabinet Grotesk + Syne Mono
```
**Output**: @import declarations + CSS font tokens + usage rules

---

### `/imagery [keyword/style]`
Sourcing premium imagery from PREMIUM_IMAGERY.md
```
/imagery luxury         → Architectural white + gold + minimal
/imagery tech           → Dark neon + abstract connectivity
/imagery organic        → Linen + nature + soft earth
/imagery 30             → Images matching Aurora style (#30)
```
**Output**: Optimized Unsplash URL + CSS "Wash" container + object-fit rules

---

### `/style-mix [style-a] + [style-b]`
Blend two style aesthetics
```
/style-mix 28 + 16   → Glassmorphism + Synthwave
/style-mix 40 + 21   → Japandi + Minimalism
/style-mix 29 + 9    → Cybercore + Constructivism
```
**Output**: Hybrid design spec with resolved conflicts

---

## 🎬 ANIMATION COMMANDS

### `/animate [type]`
Apply animation from 100_ANIMATIONS.md
```
/animate gsap-reveal        → Staggered GSAP content reveal
/animate text-scramble      → TextPlugin character scramble
/animate morph              → SVG path morphing
/animate parallax           → Layered parallax on scroll
/animate magnetic           → Magnetic cursor interaction
/animate liquid             → CSS border-radius blob animation
/animate glitch             → RGB channel split glitch
/animate stagger            → Anime.js stagger cascade  
/animate kinetic-type       → Word-by-word text reveal
/animate particle-field     → Canvas particle network
/animate neon-glow          → Pulsing neon light effect
/animate 3d-card            → Perspective tilt on hover
/animate lottie [url]       → Embed Lottie animation
/animate framer [variant]   → Framer Motion variant
/animate counter            → Animated number counter
/animate loader             → Page loading animation
```
**Output**: Ready-to-paste JS/JSX code with dependencies noted

---

### `/scroll [effect]`
Apply scroll effect (see SCROLL_EFFECTS.md)
```
/scroll reveal              → ScrollTrigger fade+translate reveal
/scroll pin-section         → Pin a section during scroll
/scroll horizontal          → Horizontal scroll gallery
/scroll parallax-hero       → Hero background parallax
/scroll text-split          → Character-level scroll animation
/scroll progress-bar        → Scroll progress indicator
/scroll sticky-panels       → Multiple sticky content panels
/scroll scrub-animation     → Animation tied to scroll position
/scroll locomotive          → Full Locomotive Scroll setup
/scroll lenis               → Lenis smooth scroll setup
/scroll zoom-sequence       → Zoom in/out on scroll
/scroll draw-path           → SVG path drawing on scroll
```
**Output**: GSAP ScrollTrigger code + Lenis integration

---

### `/gsap [pattern]`
Specific GSAP patterns from GSAP_ANIMATIONS.md
```
/gsap timeline [name]       → Create named GSAP timeline
/gsap stagger               → gsap.from with stagger config
/gsap pin [selector]        → ScrollTrigger pin setup
/gsap scrub [selector]      → Scrub animation config
/gsap split-text            → GSAP SplitText + reveal
/gsap from                  → gsap.from template
/gsap to                    → gsap.to template
/gsap fromTo                → gsap.fromTo template
```

---

## 🧩 COMPONENT COMMANDS

### `/component [name] (style) (dark|light)`
Generate premium components
```
/component hero              → Full hero section
/component hero magazine     → Editorial hero variant
/component hero split        → 50/50 text+visual hero
/component hero fullscreen   → Full-viewport immersive
/component nav               → Standard sticky nav
/component nav minimal       → Minimal floating nav
/component nav dark          → Dark transparent nav
/component feature-grid      → 3-column feature grid
/component bento             → Bento box layout
/component pricing           → 3-tier pricing cards
/component pricing dark      → Dark pricing
/component testimonials      → Quote card carousel
/component testimonials grid → Masonry testimonial grid
/component stats             → Animated counter row
/component cta               → CTA banner section
/component cta fullbleed     → Full-bleed CTA
/component footer            → Premium footer
/component faq               → Accordion FAQ
/component gallery           → Masonry image gallery
/component form-contact      → Contact form
/component form-signup       → Email signup
/component card              → Universal card component
/component modal             → Animated modal
/component tabs              → Tab navigation component
/component timeline          → Vertical timeline
/component loader            → Page preloader animation
/component cursor            → Custom cursor effect
/component cookie-banner     → GDPR-style cookie bar
/component notification      → Toast notification
```

---

## 📄 PAGE COMMANDS

### `/page [type]`
Generate a full page with all sections
```
/page saas-landing          → SaaS product landing page
/page agency                → Creative agency homepage
/page portfolio             → Designer/developer portfolio
/page ecommerce             → Product/store landing
/page startup               → Startup launch page
/page personal-brand        → Personal website
/page blog                  → Blog/editorial homepage
/page pricing               → Dedicated pricing page
/page about                 → About/team page
/page case-study            → Project case study
/page contact               → Contact page
/page coming-soon           → Coming soon / waitlist
/page error-404             → Custom 404 page
/page maintenance           → Maintenance page
```

---

## 📊 LAYOUT COMMANDS

### `/layout [type]`
Apply a layout system (see SITEMAP_LAYOUTS.md)
```
/layout editorial           → Magazine-style editorial
/layout dashboard           → App dashboard
/layout campaign            → Marketing campaign
/layout storytelling        → Scroll-driven narrative
/layout catalog             → Product grid catalog
/layout immersive           → Full-screen takeovers
/layout brutalist           → Grid-visible raw layout
/layout luxury              → Slow, ceremonial
/layout split               → 50/50 split compositions
/layout asymmetric          → Grid-breaking asymmetry
/layout centered            → Centered single-column
```

---

## 🧠 MARKETING COMMANDS

### `/marketing`
Apply full marketing/conversion layer to current design
- Rewrites headlines with conversion formulas
- Adds social proof elements
- Optimizes CTA placement and copy
- Adds trust signals
- Structures content as PAS/AIDA

### `/headline [context]`
Generate headlines using conversion formulas
```
/headline saas-productivity  → SaaS benefit headlines
/headline agency-portfolio   → Agency credibility headlines  
/headline ecommerce          → Product desire headlines
```

### `/cta [action]`
Generate specific CTA copy (no generic "Learn More")
```
/cta signup    → Specific signup CTA variants
/cta download  → Download offer CTAs
/cta trial     → Free trial CTAs
/cta contact   → Consultation/contact CTAs
```

---

## 🔍 AUDIT COMMANDS

### `/evaluate`
Run full quality rubric — returns score + action plan
```
/evaluate current           → Score the design just produced
/evaluate typography        → Typography-only audit
/evaluate color             → Color system audit
/evaluate motion            → Animation audit
/evaluate conversion        → Marketing effectiveness audit
/evaluate accessibility     → WCAG audit
```

### `/compare [style-a] [style-b]`
Compare two style approaches for a given use case

### `/debug`
Identify what's making the design feel generic and fix it

---

## 🤖 AGENT COMMANDS

### `/agent [agent-name] [context]`
Spawn a specific sub-agent (see AGENT.md)
```
/agent visual-director      → Make aesthetic decisions
/agent motion-engineer      → Implement animations
/agent copy-strategist      → Write conversion copy
/agent scroll-architect     → Design scroll narrative
/agent color-psychologist   → Deep palette analysis
/agent typography-curator   → Font system decisions
/agent component-builder    → Build specific component
/agent quality-auditor      → Full audit
/agent brief-analyst        → Parse vague brief
```

### `/orchestrate [description]`
Trigger full director agent orchestration
```
/orchestrate "Build a complete dark SaaS landing page for a project management tool targeting remote teams. Feel: powerful + organized + calm."
```
**This triggers the full agent tree: brief → visual → copy → motion → build → audit**

---

## ⚙️ CONFIGURATION COMMANDS

### `/set [option] [value]`
Set global preferences
```
/set theme dark             → Default to dark theme
/set theme light            → Default to light theme
/set framework react        → Use React/JSX output
/set framework html         → Use vanilla HTML/CSS/JS
/set icons phosphor         → Set Phosphor as icon default
/set motion gsap            → Set GSAP as motion default
/set motion framer          → Set Framer Motion as default
/set motion anime           → Set Anime.js as default
/set complexity premium     → Maximum quality mode
/set complexity quick       → Fast prototype mode
```

### `/reset`
Clear all settings, return to defaults

---

## 💡 CHAINING COMMANDS
Commands can be chained for complex outputs:
```
/design 28 + /palette innovation + /animate particle-field + /page saas-landing

→ Glassmorphism SaaS landing with electric innovation palette and particle background
```

---

## 📌 QUICK REFERENCE CARD

```
MOST USED COMMANDS:
──────────────────────────────
/design [1-100]      → Style
/palette [emotion]   → Colors
/animate [type]      → Motion  
/scroll [effect]     → Scroll
/component [name]    → Component
/page [type]         → Full page
/evaluate            → Audit
/orchestrate [brief] → Full build
──────────────────────────────
```
