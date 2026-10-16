# 🌀 ANIME.JS COMPLETE PATTERNS
**Lightweight, powerful animation for stagger, SVG, and DOM properties**

---

## SETUP
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/animejs/3.2.1/anime.min.js"></script>
```
```javascript
// npm: import anime from 'animejs/lib/anime.es.js';
```

---

## PATTERN 1: STAGGERED LIST REVEAL
```javascript
anime({
  targets: '.list-item',
  translateY: [40, 0],
  opacity: [0, 1],
  duration: 700,
  delay: anime.stagger(80, { start: 200 }),
  easing: 'easeOutExpo',
});

// Grid stagger (radiating from center)
anime({
  targets: '.grid-card',
  scale: [0.85, 1],
  opacity: [0, 1],
  duration: 600,
  delay: anime.stagger(60, { grid: [3, 3], from: 'center' }),
  easing: 'easeOutElastic(1, .8)',
});
```

---

## PATTERN 2: SVG PATH MORPHING
```javascript
// Morph between two SVG paths
anime({
  targets: '#morphing-shape path',
  d: [
    { value: 'M10 80 C 40 10, 65 10, 95 80 S 150 150, 180 80' },
    { value: 'M10 80 C 40 150, 65 150, 95 80 S 150 10, 180 80' },
  ],
  duration: 2000,
  loop: true,
  direction: 'alternate',
  easing: 'easeInOutSine',
});

// Blob shape morphing
const blobPaths = [
  'M50,10 C80,10 90,30 90,50 C90,70 80,90 50,90 C20,90 10,70 10,50 C10,30 20,10 50,10',
  'M50,5 C85,15 95,35 90,55 C85,75 70,90 50,90 C30,88 10,72 8,52 C6,32 18,10 50,5',
];
anime({
  targets: '#blob',
  d: blobPaths,
  duration: 3000,
  loop: true,
  direction: 'alternate',
  easing: 'easeInOutQuart',
});
```

---

## PATTERN 3: TYPEWRITER WITH CURSOR
```javascript
const phrases = ['Premium Interfaces', 'World-Class Motion', 'Agency-Level Design'];
let phraseIndex = 0;

function typePhrase(phrase) {
  const el = document.querySelector('.typewriter');
  el.textContent = '';
  
  anime({
    targets: { len: 0 },
    len: phrase.length,
    round: 1,
    easing: 'linear',
    duration: phrase.length * 60,
    update: anim => {
      el.textContent = phrase.substring(0, anim.animatables[0].target.len);
    },
    complete: () => setTimeout(deletePhrase, 1500)
  });
}

function deletePhrase() {
  const el = document.querySelector('.typewriter');
  anime({
    targets: { len: el.textContent.length },
    len: 0, round: 1, easing: 'linear', duration: 400,
    update: anim => {
      el.textContent = el.textContent.substring(0, anim.animatables[0].target.len);
    },
    complete: () => {
      phraseIndex = (phraseIndex + 1) % phrases.length;
      setTimeout(() => typePhrase(phrases[phraseIndex]), 300);
    }
  });
}
typePhrase(phrases[0]);
```

---

## PATTERN 4: PARTICLE BURST ON CLICK
```javascript
function createBurst(x, y) {
  const particles = 12;
  const colors = ['#7C3AED', '#00D9B8', '#F472B6'];
  
  for (let i = 0; i < particles; i++) {
    const el = document.createElement('div');
    el.style.cssText = `
      position: fixed; left: ${x}px; top: ${y}px;
      width: 8px; height: 8px; border-radius: 50%;
      background: ${colors[i % colors.length]};
      pointer-events: none; z-index: 9999;
      transform: translate(-50%, -50%);
    `;
    document.body.appendChild(el);
    
    const angle = (i / particles) * Math.PI * 2;
    const distance = 60 + Math.random() * 60;
    
    anime({
      targets: el,
      translateX: Math.cos(angle) * distance,
      translateY: Math.sin(angle) * distance,
      opacity: [1, 0],
      scale: [1, 0],
      duration: 700 + Math.random() * 300,
      easing: 'easeOutExpo',
      complete: () => el.remove(),
    });
  }
}

document.querySelector('.btn-burst').addEventListener('click', e => {
  createBurst(e.clientX, e.clientY);
});
```

---

## PATTERN 5: LOADING ANIMATION
```javascript
// Elegant page loader
const loader = anime.timeline({ easing: 'easeInOutExpo' });

loader
  .add({
    targets: '.loader-line',
    scaleX: [0, 1], transformOrigin: ['0% 50%', '0% 50%'],
    duration: 1200,
  })
  .add({
    targets: '.loader-logo',
    opacity: [0, 1], translateY: [20, 0],
    duration: 600,
  }, '-=400')
  .add({
    targets: '.loader-percent',
    innerHTML: [0, 100],
    round: 1,
    duration: 1200,
  }, 0)
  .add({
    targets: '.loader',
    translateY: '-100%',
    duration: 800,
    delay: 400,
    complete: () => document.querySelector('.loader').style.display = 'none'
  });
```

---

## PATTERN 6: FLOATING ELEMENTS
```javascript
// Organic floating (multiple elements at different speeds)
document.querySelectorAll('.float-element').forEach((el, i) => {
  anime({
    targets: el,
    translateY: [
      { value: -15 - i * 5, duration: 1800 + i * 200, easing: 'easeInOutSine' },
      { value: 0, duration: 1800 + i * 200, easing: 'easeInOutSine' },
    ],
    translateX: [
      { value: 8 + i * 3, duration: 2200 + i * 150, easing: 'easeInOutSine' },
      { value: 0, duration: 2200 + i * 150, easing: 'easeInOutSine' },
    ],
    rotate: [
      { value: 3, duration: 2000, easing: 'easeInOutSine' },
      { value: -3, duration: 2000, easing: 'easeInOutSine' },
    ],
    loop: true,
    direction: 'alternate',
    delay: i * 300,
  });
});
```

---

## PATTERN 7: BACKGROUND GRADIENT SHIFT
```javascript
const colors = [
  { r: 124, g: 58, b: 237 },   // violet
  { r: 0, g: 217, b: 184 },    // teal
  { r: 244, g: 114, b: 182 },  // pink
  { r: 245, g: 158, b: 11 },   // amber
];
let current = 0;

function shiftGradient() {
  const next = (current + 1) % colors.length;
  const c = colors[current];
  const n = colors[next];
  
  anime({
    targets: { r: c.r, g: c.g, b: c.b },
    r: n.r, g: n.g, b: n.b,
    duration: 3000,
    easing: 'easeInOutSine',
    update: anim => {
      const t = anim.animatables[0].target;
      document.querySelector('.animated-bg').style.background =
        `radial-gradient(ellipse 70% 60% at 30% 40%, rgba(${Math.round(t.r)},${Math.round(t.g)},${Math.round(t.b)},0.3), transparent)`;
    },
    complete: () => { current = next; shiftGradient(); }
  });
}
shiftGradient();
```

---

## PATTERN 8: SCROLL-TRIGGERED WITH IntersectionObserver
```javascript
const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const el = entry.target;
      const delay = parseInt(el.dataset.delay) || 0;
      
      anime({
        targets: el,
        translateY: [50, 0],
        opacity: [0, 1],
        duration: 800,
        delay: delay,
        easing: 'easeOutExpo',
      });
      observer.unobserve(el);
    }
  });
}, { threshold: 0.15 });

document.querySelectorAll('.anime-reveal').forEach(el => observer.observe(el));
```

---

## PATTERN 9: NUMBER MORPHING (Odometer Effect)
```javascript
function morphNumber(el, from, to) {
  anime({
    targets: el,
    innerHTML: [from, to],
    round: 1,
    duration: 2000,
    easing: 'easeInOutExpo',
    update: a => {
      el.innerHTML = Number(a.animatables[0].target.innerHTML).toLocaleString();
    }
  });
}
// Usage: morphNumber(document.querySelector('.stat'), 0, 50000)
```

---

## PATTERN 10: NAV LINK HOVER (Stagger reveal)
```javascript
document.querySelectorAll('.nav-item').forEach(item => {
  const underline = item.querySelector('.nav-underline');
  
  item.addEventListener('mouseenter', () => {
    anime({ targets: underline, scaleX: [0, 1], transformOrigin: ['0%', '0%'], duration: 300, easing: 'easeOutExpo' });
  });
  item.addEventListener('mouseleave', () => {
    anime({ targets: underline, scaleX: [1, 0], transformOrigin: ['100%', '100%'], duration: 200, easing: 'easeInExpo' });
  });
});
```
