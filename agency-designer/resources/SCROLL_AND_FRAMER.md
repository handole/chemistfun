# 🌊 SCROLL EFFECTS + FRAMER MOTION REFERENCE

---

## SCROLL EFFECTS COMPLETE LIST

### 1. Lenis Smooth Scroll (ALWAYS INCLUDE)
```javascript
import Lenis from '@studio-freight/lenis';
const lenis = new Lenis({ duration: 1.2, easing: t => Math.min(1, 1.001 - Math.pow(2, -10 * t)) });
gsap.ticker.add(time => lenis.raf(time * 1000));
gsap.ticker.lagSmoothing(0);
```

### 2. Locomotive Scroll (Alternative)
```javascript
import LocomotiveScroll from 'locomotive-scroll';
const scroll = new LocomotiveScroll({ el: document.querySelector('[data-scroll-container]'), smooth: true, lerp: 0.08 });
// HTML: <div data-scroll-container> <div data-scroll data-scroll-speed="2">Parallax</div>
```

### 3. Parallax Layers
```javascript
// Multiple depths
['[data-depth="slow"]','[data-depth="mid"]','[data-depth="fast"]'].forEach((sel, i) => {
  gsap.to(sel, { y: `${(i+1)*20}%`, ease:'none',
    scrollTrigger: { trigger:'.section', start:'top bottom', end:'bottom top', scrub:true }
  });
});
```

### 4. Text Char Reveal on Scroll
```javascript
// Requires Splitting.js
gsap.from('[data-scroll-split] .char', {
  yPercent: 120, stagger: 0.02, duration: 0.8, ease: 'power3.out',
  scrollTrigger: { trigger: '[data-scroll-split]', start: 'top 80%' }
});
```

### 5. Image Stack Reveal
```javascript
gsap.from('.img-stack .img', {
  y: 60, opacity: 0, stagger: 0.12, duration: 0.8, ease: 'power3.out',
  scrollTrigger: { trigger: '.img-stack', start: 'top 75%' }
});
```

### 6. Counter + Stats
```javascript
ScrollTrigger.create({ trigger: '.stats', start: 'top 80%', once: true,
  onEnter: () => { /* trigger counters */ }
});
```

### 7. Background Color Change
```javascript
const sections = [{el: '#hero', color: '#04040A'}, {el: '#features', color: '#080814'}, {el: '#testimonials', color: '#040410'}];
sections.forEach(s => {
  ScrollTrigger.create({ trigger: s.el, start: 'top 50%', end: 'bottom 50%',
    onEnter: () => gsap.to('body', { backgroundColor: s.color, duration: 0.8 }),
    onEnterBack: () => gsap.to('body', { backgroundColor: s.color, duration: 0.8 }),
  });
});
```

---

## FRAMER MOTION — REACT PATTERNS

### Setup
```bash
npm install framer-motion
```

### 1. Page Entry Animation
```jsx
import { motion } from 'framer-motion';

const pageVariants = {
  initial: { opacity: 0, y: 20 },
  enter: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] } },
  exit: { opacity: 0, y: -20, transition: { duration: 0.3 } }
};

export default function Page() {
  return (
    <motion.div variants={pageVariants} initial="initial" animate="enter" exit="exit">
      {/* page content */}
    </motion.div>
  );
}
```

### 2. Stagger Container + Children
```jsx
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1, delayChildren: 0.2 }
  }
};
const item = {
  hidden: { y: 40, opacity: 0 },
  show: { y: 0, opacity: 1, transition: { type: 'spring', stiffness: 100, damping: 15 } }
};

<motion.ul variants={container} initial="hidden" whileInView="show" viewport={{ once: true, amount: 0.2 }}>
  {items.map(i => <motion.li key={i} variants={item}>{i}</motion.li>)}
</motion.ul>
```

### 3. Scroll-Linked Animation (useScroll + useTransform)
```jsx
import { useScroll, useTransform, motion } from 'framer-motion';

function ParallaxHero() {
  const { scrollY } = useScroll();
  const y = useTransform(scrollY, [0, 500], [0, 150]);
  const opacity = useTransform(scrollY, [0, 300], [1, 0]);

  return (
    <div className="hero">
      <motion.div className="hero-bg" style={{ y }} />
      <motion.div className="hero-content" style={{ opacity }} />
    </div>
  );
}
```

### 4. Gesture Interactions
```jsx
// Magnetic card
<motion.div
  className="card"
  whileHover={{ scale: 1.03, y: -4 }}
  whileTap={{ scale: 0.98 }}
  transition={{ type: 'spring', stiffness: 400, damping: 17 }}
>

// Button with click animation
<motion.button
  className="btn-primary"
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  transition={{ type: 'spring', stiffness: 500, damping: 20 }}
>
```

### 5. AnimatePresence (Modal, Notifications)
```jsx
import { AnimatePresence, motion } from 'framer-motion';

<AnimatePresence>
  {isOpen && (
    <motion.div
      className="modal-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <motion.div
        className="modal"
        initial={{ scale: 0.8, opacity: 0, y: 40 }}
        animate={{ scale: 1, opacity: 1, y: 0 }}
        exit={{ scale: 0.9, opacity: 0, y: 20 }}
        transition={{ type: 'spring', stiffness: 300, damping: 25 }}
      >
        {children}
      </motion.div>
    </motion.div>
  )}
</AnimatePresence>
```

### 6. Layout Animations (Shared Element)
```jsx
// Expanding card
<motion.div layoutId="card-1" className="card-small" onClick={() => setSelected(true)}>
  <motion.h3 layoutId="card-1-title">Title</motion.h3>
</motion.div>

{selected && (
  <motion.div layoutId="card-1" className="card-expanded">
    <motion.h3 layoutId="card-1-title">Title</motion.h3>
    <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }}>Full content</motion.p>
  </motion.div>
)}
```

### 7. Scroll Progress Indicator
```jsx
import { useScroll, useSpring, motion } from 'framer-motion';

function ProgressBar() {
  const { scrollYProgress } = useScroll();
  const scaleX = useSpring(scrollYProgress, { stiffness: 100, damping: 30 });
  return <motion.div className="progress-bar" style={{ scaleX }} />;
}
```

---

## 100 ANIMATION STYLES — GSAP/ANIME/FRAMER IMPLEMENTATION

### Quick Reference — Which Library for Which Effect

| Animation (from list) | Library | Pattern |
|----------------------|---------|---------|
| 51. Traditional 2D | Anime.js | sprite steps() |
| 52. Digital 2D | GSAP | timeline tweens |
| 53. 3D Animation | Three.js + GSAP | WebGL + scrub |
| 56. Motion Graphics | GSAP | SVG timeline |
| 57. Kinetic Typography | GSAP + Splitting.js | char stagger |
| 62. Morphing | GSAP MorphSVG or Anime.js d: | path morphing |
| 69. HUD Animation | CSS @keyframes + GSAP | bracket anim |
| 70. Plexus | Canvas API | particle lines |
| 71. Fluid Simulation | CSS blob + Anime.js | border-radius |
| 72. Glitch | CSS clip + GSAP | RGB offset |
| 73. Parallax | GSAP ScrollTrigger | scrub depth |
| 74. Bokeh | CSS filter: blur | blur circles |
| 76. Neon Glow | CSS box-shadow + Anime.js | pulse glow |
| 80. Particle Systems | Canvas + Anime.js | particle spawn |
| 82. Low Poly | Three.js or SVG | geometry |
| 87. Cinemagraph | Single CSS animation | isolated loop |
| 89. Liquid Motion | Anime.js border-radius | blob morph |
| 92. Lottie | lottie-web library | JSON playback |
| 93. Path Animation | CSS offset-path | motion path |
| 94. Ease-In/Out | Framer Motion spring | natural ease |
| 96. Staggered | Anime.js stagger() | delay cascade |
| 98. Retro Grain | SVG feTurbulence | noise filter |
| 99. Masking & Reveals | GSAP clipPath | clip animation |
| 100. Squash & Stretch | GSAP scale + ease | elastic bounce |
