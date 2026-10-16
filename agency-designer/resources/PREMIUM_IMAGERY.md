# PREMIUM IMAGERY & VISUAL ASSETS
**Phase 3.4 — Sourcing and Styling Agency-Grade Visuals**

> "A stock photo is a liability. A styled visual is an asset. Never use raw imagery without a brand veneer."

---

## 🚀 1. DYNAMIC API TEMPLATES

Use these templates to fetch optimized, high-resolution imagery.

### 1.1 Unsplash (Primary — Photos)
**Best for**: High-end aesthetic photos.  
**Template**: `https://images.unsplash.com/photo-{ID}?w={WIDTH}&q={QUALITY}&fit=crop`  
**Keyword Search**: `https://source.unsplash.com/featured/{WIDTH}x{HEIGHT}/?{KEYWORDS}` *(Note: Unsplash Source is legacy; use specific Photo IDs for production or `images.unsplash.com` with search terms in query).*

**Recommended Keyword Pattern**:  
`https://images.unsplash.com/featured/?{style},{mood},{subject}`

### 1.2 Pexels (Secondary — Video)
**Best for**: Cinematic hero backgrounds and video loops.  
**Template**: `https://www.pexels.com/search/video/{keywords}/`  
**Video Integration API**: `https://player.vimeo.com/external/{id}.hd.mp4?s={hash}&profile_id={id}`

---

## 🎨 2. MOOD-TO-KEYWORD MAPPING

Always combine 3 keywords for the best results: `[STYLE] + [MOOD] + [SUBJECT]`.

| Style Category | Keywords | Examples |
| :--- | :--- | :--- |
| **Luxury / Premium** | minimalist, white, architecture, gold, satin, glass | [View Luxury](https://images.unsplash.com/featured/?minimalist,architecture) |
| **Tech / SaaS** | abstract, connectivity, dark, neon, interface, server | [View Tech](https://images.unsplash.com/featured/?tech,abstract) |
| **Cyberpunk / Retro** | neon, rain, night, synthwave, glitch, urban | [View Cyber](https://images.unsplash.com/featured/?neon,night) |
| **Editorial / Fashion** | portrait, shadow, grain, magazine, high-contrast, studio | [View Fashion](https://images.unsplash.com/featured/?fashion,portrait) |
| **Organic / Sustainable** | nature, fabric, linen, earth, leaf, grain, soft | [View Organic](https://images.unsplash.com/featured/?nature,linen) |
| **Dashboard / Data** | blueprint, grid, top-down, clean, organized, technical | [View Data](https://images.unsplash.com/featured/?grid,architecture) |

---

## 🪄 3. THE "PREMIUM WASH" (CSS STANDARDS)

**NEVER** use an image without at least one of these treatments.

### 3.1 The Brand Overlay (Linear)
```css
/* Hero section background */
.hero-image {
  background-image: 
    linear-gradient(to bottom, rgba(0,0,0,0.8), rgba(0,0,0,0.3)), /* Darkening for text */
    url('https://images.unsplash.com/featured/?premium,architecture');
  background-size: cover;
  background-position: center;
}
```

### 3.2 The Glassmorphism Mask
```css
.card-content {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(12px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
```

### 3.3 The Grain Veneer (Universal)
```css
.premium-bg::after {
  content: "";
  position: absolute;
  inset: 0;
  background-image: url("data:image/svg+xml,..."); /* See SKILL.md for SVG grain */
  opacity: 0.03;
  pointer-events: none;
}
```

---

## 🛠 4. AI INSTRUCTIONS (How to Prompt)

When adding an image, the AI MUST:
1. Identify the **Mood Style Number** from `100_GRAPHIC_STYLES.md`.
2. Select 3 keywords from the mapping above.
3. Generate the CSS container with an appropriate **Brand Overlay**.
4. Apply `loading="lazy"` for all images below the fold.
5. Use `object-fit: cover` for container-filling layouts.
