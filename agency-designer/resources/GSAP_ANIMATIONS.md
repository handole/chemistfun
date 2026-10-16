# ⚡ GSAP + ScrollTrigger + Lenis COMPLETE COOKBOOK
**Production-ready animation patterns for agency-level interfaces**

---

## SETUP — ALWAYS USE THIS INITIALIZATION

```html
<!-- CDN Imports (HTML projects) -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/TextPlugin.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/splitting@1.0.6/dist/splitting.min.js"></script>
<script src="https://cdn.jsdelivr.net/gh/studio-freight/lenis@1.0.42/bundled/lenis.min.js"></script>
```

```javascript
// MASTER INITIALIZATION
gsap.registerPlugin(ScrollTrigger, TextPlugin);

// Smooth scroll with Lenis
const lenis = new Lenis({
  duration: 1.2,
  easing: t => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
  direction: 'vertical',
  gestureDirection: 'vertical',
  smooth: true,
  mouseMultiplier: 1,
  smoothTouch: false,
  touchMultiplier: 2,
});

function raf(time) { lenis.raf(time); requestAnimationFrame(raf); }
requestAnimationFrame(raf);

// Connect Lenis to ScrollTrigger
lenis.on('scroll', ScrollTrigger.update);
gsap.ticker.add(time => lenis.raf(time * 1000));
gsap.ticker.lagSmoothing(0);

// Splitting.js for text animations
Splitting();
```

---

## PATTERN 1: PAGE LOAD MASTER SEQUENCE

```javascript
// The cinematic page entrance
const masterTimeline = gsap.timeline({ defaults: { ease: 'power3.out' } });

masterTimeline
  // Preloader fade out
  .to('.preloader', { opacity: 0, duration: 0.6, onComplete: () => {
    document.querySelector('.preloader').style.display = 'none';
  }})
  // Nav slides down
  .from('nav', { y: -80, opacity: 0, duration: 0.8 }, '-=0.3')
  // Hero badge/eyebrow
  .from('.hero-badge', { y: 20, opacity: 0, duration: 0.5 }, '-=0.4')
  // Main headline chars
  .from('.hero-title .char', {
    y: 100, opacity: 0, rotationX: -60,
    stagger: 0.025, duration: 0.7,
    transformOrigin: '50% 50% -50px'
  }, '-=0.2')
  // Sub-headline words
  .from('.hero-sub .word', {
    y: 20, opacity: 0,
    stagger: 0.04, duration: 0.5
  }, '-=0.4')
  // CTA buttons
  .from('.hero-cta > *', {
    y: 20, opacity: 0, scale: 0.95,
    stagger: 0.1, duration: 0.4
  }, '-=0.3')
  // Hero visual / image
  .from('.hero-visual', {
    x: 60, opacity: 0, duration: 0.8
  }, '-=0.8')
  // Scroll indicator
  .from('.scroll-indicator', {
    y: -20, opacity: 0, duration: 0.5
  }, '-=0.2');
```

---

## PATTERN 2: SCROLL REVEAL (Universal)

```javascript
// Apply to ANY element with class "reveal"
const revealElements = gsap.utils.toArray('.reveal');

revealElements.forEach(el => {
  const direction = el.dataset.direction || 'up'; // up, down, left, right, scale
  
  const fromVars = {
    up:    { y: 60, opacity: 0 },
    down:  { y: -60, opacity: 0 },
    left:  { x: -60, opacity: 0 },
    right: { x: 60, opacity: 0 },
    scale: { scale: 0.85, opacity: 0 },
    fade:  { opacity: 0 },
  }[direction];
  
  gsap.from(el, {
    ...fromVars,
    duration: 0.9,
    ease: 'power3.out',
    scrollTrigger: {
      trigger: el,
      start: 'top 85%',
      end: 'top 40%',
      toggleActions: 'play none none none',
    }
  });
});

// Staggered children reveal
gsap.utils.toArray('.reveal-stagger').forEach(container => {
  gsap.from(container.children, {
    y: 40, opacity: 0,
    stagger: 0.1, duration: 0.7,
    ease: 'power3.out',
    scrollTrigger: {
      trigger: container,
      start: 'top 80%',
    }
  });
});
```

---

## PATTERN 3: TEXT ANIMATIONS

```javascript
// 3A: Character-level headline reveal (requires Splitting.js)
// HTML: <h1 data-splitting>Your Headline Here</h1>
gsap.from('[data-splitting] .char', {
  y: 110, opacity: 0, rotationZ: 8,
  stagger: 0.02, duration: 0.7,
  ease: 'power4.out',
  scrollTrigger: { trigger: '.headline-section', start: 'top 75%' }
});

// 3B: Word-by-word reveal
gsap.from('[data-splitting] .word', {
  y: 40, opacity: 0,
  stagger: 0.05, duration: 0.5,
  ease: 'power3.out',
  scrollTrigger: { trigger: '.text-section', start: 'top 80%' }
});

// 3C: Text scramble using TextPlugin
const scrambleTimeline = gsap.timeline({ repeat: -1, repeatDelay: 2 });
const phrases = ["Build Premium UI", "Ship Faster", "Design Without Limits"];
let current = 0;

function animatePhrase() {
  const el = document.querySelector('.scramble-text');
  gsap.to(el, {
    duration: 1.5,
    text: {
      value: phrases[current % phrases.length],
      delimiter: '',
      speed: 1,
    },
    ease: 'none',
    onComplete: () => {
      current++;
      setTimeout(animatePhrase, 2000);
    }
  });
}
animatePhrase();

// 3D: Gradient text shimmer on scroll
gsap.to('.gradient-text', {
  backgroundPosition: '200% center',
  ease: 'none',
  scrollTrigger: {
    trigger: '.gradient-text',
    start: 'top bottom',
    end: 'bottom top',
    scrub: 1,
  }
});
```

---

## PATTERN 4: HERO PARALLAX

```javascript
// Multi-layer parallax
gsap.to('.hero-bg-layer-1', {
  y: '30%', ease: 'none',
  scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: 1 }
});
gsap.to('.hero-bg-layer-2', {
  y: '15%', ease: 'none',
  scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: 1 }
});
gsap.to('.hero-content', {
  y: '-20%', opacity: 0.5, ease: 'none',
  scrollTrigger: { trigger: '.hero', start: 'top top', end: 'center top', scrub: 1 }
});
```

---

## PATTERN 5: PINNED FEATURE SHOWCASE

```javascript
// Pin a section while inner panels animate
const panels = gsap.utils.toArray('.feature-panel');

ScrollTrigger.create({
  trigger: '.features-pinned',
  start: 'top top',
  end: `+=${panels.length * 100}%`,
  pin: true,
  pinSpacing: true,
  onUpdate: self => {
    const progress = self.progress;
    const panelIndex = Math.floor(progress * panels.length);
    const panelProgress = (progress * panels.length) % 1;
    
    panels.forEach((panel, i) => {
      if (i < panelIndex) {
        gsap.set(panel, { opacity: 0, x: '-100%' });
      } else if (i === panelIndex) {
        gsap.set(panel, { opacity: 1, x: `${-panelProgress * 100}%` });
      } else {
        gsap.set(panel, { opacity: 0, x: '100%' });
      }
    });
  }
});

// Simpler: Timeline-based panel transitions
const tl = gsap.timeline({
  scrollTrigger: {
    trigger: '.features-section',
    start: 'top top',
    end: '+=400%',
    scrub: 1,
    pin: true,
  }
});

tl.to('.panel-1', { xPercent: -100, opacity: 0, duration: 1 })
  .from('.panel-2', { xPercent: 100, opacity: 0, duration: 1 }, '<')
  .to('.panel-2', { xPercent: -100, opacity: 0, duration: 1 })
  .from('.panel-3', { xPercent: 100, opacity: 0, duration: 1 }, '<');
```

---

## PATTERN 6: HORIZONTAL SCROLL GALLERY

```javascript
const sections = gsap.utils.toArray('.h-panel');
const container = document.querySelector('.h-scroll-container');

gsap.to(sections, {
  xPercent: -100 * (sections.length - 1),
  ease: 'none',
  scrollTrigger: {
    trigger: '.h-scroll-wrapper',
    pin: true,
    scrub: 1,
    snap: 1 / (sections.length - 1),
    end: () => `+=${container.offsetWidth}`,
  }
});
```

```css
.h-scroll-wrapper { overflow: hidden; }
.h-scroll-container { display: flex; flex-wrap: nowrap; width: fit-content; }
.h-panel { min-width: 100vw; height: 100vh; flex-shrink: 0; }
```

---

## PATTERN 7: COUNTER ANIMATION

```javascript
gsap.utils.toArray('[data-count]').forEach(el => {
  const target = parseInt(el.dataset.count);
  const prefix = el.dataset.prefix || '';
  const suffix = el.dataset.suffix || '';
  
  gsap.from({ val: 0 }, {
    val: target,
    duration: 2,
    ease: 'power2.out',
    scrollTrigger: { trigger: el, start: 'top 85%' },
    onUpdate: function() {
      el.textContent = prefix + Math.round(this.targets()[0].val).toLocaleString() + suffix;
    }
  });
});
```

---

## PATTERN 8: SCROLL-DRIVEN PROGRESS LINE

```javascript
// Animated line that draws as user scrolls
gsap.to('.progress-line', {
  scaleX: 1, transformOrigin: 'left center', ease: 'none',
  scrollTrigger: { trigger: 'body', start: 'top top', end: 'bottom bottom', scrub: 0.5 }
});

// Section progress dots
const sections = gsap.utils.toArray('.section');
const dots = gsap.utils.toArray('.nav-dot');

sections.forEach((section, i) => {
  ScrollTrigger.create({
    trigger: section,
    start: 'top 50%',
    end: 'bottom 50%',
    onEnter: () => dots[i]?.classList.add('active'),
    onLeave: () => dots[i]?.classList.remove('active'),
    onEnterBack: () => dots[i]?.classList.add('active'),
    onLeaveBack: () => dots[i]?.classList.remove('active'),
  });
});
```

---

## PATTERN 9: MAGNETIC ELEMENTS

```javascript
document.querySelectorAll('.magnetic').forEach(el => {
  const inner = el.querySelector('.magnetic-inner') || el;
  
  el.addEventListener('mousemove', e => {
    const rect = el.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    
    gsap.to(inner, {
      x: x * 0.35,
      y: y * 0.35,
      duration: 0.3,
      ease: 'power2.out',
    });
  });
  
  el.addEventListener('mouseleave', () => {
    gsap.to(inner, { x: 0, y: 0, duration: 0.6, ease: 'elastic.out(1, 0.5)' });
  });
});
```

---

## PATTERN 10: SVG PATH DRAWING

```javascript
// Draw SVG on scroll
gsap.utils.toArray('.draw-path').forEach(path => {
  const length = path.getTotalLength();
  gsap.set(path, { strokeDasharray: length, strokeDashoffset: length });
  
  gsap.to(path, {
    strokeDashoffset: 0, ease: 'none',
    scrollTrigger: {
      trigger: path,
      start: 'top 80%',
      end: 'bottom 20%',
      scrub: 1,
    }
  });
});
```

---

## PATTERN 11: IMAGE REVEAL CLIP-PATH

```javascript
// Cinematic image reveal
gsap.from('.image-reveal', {
  clipPath: 'inset(100% 0% 0% 0%)',
  duration: 1.2,
  ease: 'power4.inOut',
  scrollTrigger: { trigger: '.image-reveal', start: 'top 80%' }
});

// Wipe left to right
gsap.from('.image-wipe', {
  clipPath: 'inset(0% 100% 0% 0%)',
  duration: 1, ease: 'power3.inOut',
  scrollTrigger: { trigger: '.image-wipe', start: 'top 75%' }
});

// Scale + reveal
const tl = gsap.timeline({
  scrollTrigger: { trigger: '.img-scale-reveal', start: 'top 80%' }
});
tl.from('.img-scale-reveal .wrapper', { clipPath: 'inset(0% 50% 0% 50%)', duration: 1, ease: 'power4.inOut' })
  .from('.img-scale-reveal img', { scale: 1.3, duration: 1.2, ease: 'power3.out' }, 0);
```

---

## PATTERN 12: STICKY SECTION WITH PROGRESS

```javascript
// Content panel that sticks and shows progress
const sticky = document.querySelector('.sticky-section');
const progress = sticky.querySelector('.sticky-progress');
const content = gsap.utils.toArray('.sticky-content-item');

ScrollTrigger.create({
  trigger: sticky,
  start: 'top top',
  end: `+=${content.length * 400}px`,
  pin: true,
  onUpdate: self => {
    const step = Math.floor(self.progress * content.length);
    content.forEach((item, i) => {
      gsap.to(item, {
        opacity: i === step ? 1 : 0,
        y: i === step ? 0 : i < step ? -30 : 30,
        duration: 0.4,
        ease: 'power2.out'
      });
    });
    gsap.to(progress, { scaleY: self.progress, duration: 0.1 });
  }
});
```

---

## PATTERN 13: NAVBAR TRANSFORM ON SCROLL

```javascript
const nav = document.querySelector('nav');

ScrollTrigger.create({
  start: 'top -80px',
  end: 99999,
  toggleClass: { targets: 'nav', className: 'scrolled' }
});

// Advanced nav shrink
gsap.to('nav', {
  padding: '12px 40px', duration: 0.4,
  scrollTrigger: {
    trigger: 'body',
    start: '80px top',
    toggleActions: 'play none none reverse',
  }
});
```

---

## PATTERN 14: CURSOR FOLLOWER

```javascript
const cursor = document.querySelector('.cursor');
const cursorDot = document.querySelector('.cursor-dot');

let mouseX = 0, mouseY = 0;

window.addEventListener('mousemove', e => {
  mouseX = e.clientX;
  mouseY = e.clientY;
  
  gsap.to(cursorDot, { x: mouseX - 4, y: mouseY - 4, duration: 0.1 });
  gsap.to(cursor, { x: mouseX - 20, y: mouseY - 20, duration: 0.4, ease: 'power2.out' });
});

// Cursor state changes
document.querySelectorAll('a, button, .interactive').forEach(el => {
  el.addEventListener('mouseenter', () => {
    gsap.to(cursor, { scale: 2.5, opacity: 0.5, duration: 0.3 });
    gsap.to(cursorDot, { scale: 0, duration: 0.3 });
  });
  el.addEventListener('mouseleave', () => {
    gsap.to(cursor, { scale: 1, opacity: 1, duration: 0.3 });
    gsap.to(cursorDot, { scale: 1, duration: 0.3 });
  });
});
```

```css
.cursor {
  position: fixed; pointer-events: none; z-index: 9999;
  width: 40px; height: 40px; border-radius: 50%;
  border: 1.5px solid var(--clr-primary);
  transform: translate(-50%, -50%);
  mix-blend-mode: difference;
}
.cursor-dot {
  position: fixed; pointer-events: none; z-index: 9999;
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--clr-primary);
  transform: translate(-50%, -50%);
}
```

---

## PATTERN 15: SCROLL ZOOM SEQUENCE

```javascript
// Hero zooms in as user scrolls
gsap.to('.hero-image', {
  scale: 1.2, ease: 'none',
  scrollTrigger: {
    trigger: '.hero',
    start: 'top top',
    end: 'bottom top',
    scrub: true,
  }
});

// Section zooms into next section
gsap.to('.zoom-target', {
  scale: 15,
  opacity: 0,
  ease: 'power2.in',
  scrollTrigger: {
    trigger: '.zoom-section',
    start: 'top top',
    end: '+=500px',
    scrub: 1,
    pin: true,
  }
});
```
