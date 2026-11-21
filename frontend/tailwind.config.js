/** @type {import('tailwindcss').Config} */

// Ramps are HSL literals here and referenced by hsl(var(--kf-*)) in components.
// See design.md: one accent (verdigris), one graphite neutral, three status colours.
const neutral = {
  50: 'hsl(40 24% 97%)',
  100: 'hsl(40 18% 94%)',
  200: 'hsl(200 14% 88%)',
  300: 'hsl(200 12% 78%)',
  400: 'hsl(200 10% 40%)',
  500: 'hsl(200 13% 33%)',
  600: 'hsl(200 14% 30%)',
  700: 'hsl(200 16% 24%)',
  800: 'hsl(200 20% 17%)',
  900: 'hsl(200 22% 12%)',
  950: 'hsl(200 24% 8%)',
}

const accent = {
  DEFAULT: 'hsl(var(--kf-accent))',
  line: 'hsl(var(--kf-accent-line))',
  soft: 'hsl(var(--kf-accent-soft))',
  50: 'hsl(174 40% 96%)',
  100: 'hsl(174 36% 91%)',
  200: 'hsl(174 30% 82%)',
  300: 'hsl(174 28% 66%)',
  400: 'hsl(174 32% 50%)',
  500: 'hsl(174 42% 40%)',
  600: 'hsl(174 58% 27%)',
  700: 'hsl(174 60% 22%)',
  800: 'hsl(174 55% 18%)',
  900: 'hsl(174 48% 14%)',
  950: 'hsl(174 48% 9%)',
}

const success = {
  DEFAULT: 'hsl(var(--kf-success))',
  50: 'hsl(152 40% 95%)',
  100: 'hsl(152 38% 89%)',
  200: 'hsl(152 32% 79%)',
  300: 'hsl(152 28% 64%)',
  400: 'hsl(152 32% 44%)',
  500: 'hsl(152 42% 34%)',
  600: 'hsl(152 52% 27%)',
  700: 'hsl(152 54% 22%)',
  800: 'hsl(152 50% 17%)',
  900: 'hsl(152 45% 13%)',
  950: 'hsl(152 45% 9%)',
}

const warning = {
  DEFAULT: 'hsl(var(--kf-warning))',
  50: 'hsl(36 86% 95%)',
  100: 'hsl(36 82% 89%)',
  200: 'hsl(36 76% 79%)',
  300: 'hsl(36 72% 66%)',
  400: 'hsl(34 78% 48%)',
  500: 'hsl(32 76% 40%)',
  600: 'hsl(30 76% 32%)',
  700: 'hsl(28 74% 26%)',
  800: 'hsl(26 70% 20%)',
  900: 'hsl(24 66% 15%)',
  950: 'hsl(24 66% 10%)',
}

const danger = {
  DEFAULT: 'hsl(var(--kf-danger))',
  50: 'hsl(355 80% 96%)',
  100: 'hsl(355 74% 92%)',
  200: 'hsl(355 66% 84%)',
  300: 'hsl(355 60% 72%)',
  400: 'hsl(355 58% 58%)',
  500: 'hsl(355 60% 46%)',
  600: 'hsl(355 64% 38%)',
  700: 'hsl(355 64% 31%)',
  800: 'hsl(355 60% 25%)',
  900: 'hsl(355 56% 19%)',
  950: 'hsl(355 56% 12%)',
}

export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        /* Semantic surfaces and text */
        paper: 'hsl(var(--kf-paper))',
        surface: 'hsl(var(--kf-surface))',
        sunken: 'hsl(var(--kf-sunken))',
        ink: {
          DEFAULT: 'hsl(var(--kf-ink))',
          soft: 'hsl(var(--kf-ink-soft))',
          muted: 'hsl(var(--kf-ink-muted))',
          faint: 'hsl(var(--kf-ink-faint))',
        },
        line: {
          DEFAULT: 'hsl(var(--kf-line))',
          strong: 'hsl(var(--kf-line-strong))',
        },
        accent: accent,
        success: success,
        warning: warning,
        danger: danger,

        /* Kept so existing markup resolves to tokens, never to Tailwind defaults */
        chemist: {
          dark: 'hsl(var(--kf-ink))',
          darker: 'hsl(200 24% 8%)',
          navy: 'hsl(200 20% 17%)',
          card: 'hsl(var(--kf-surface))',
          bg: 'hsl(var(--kf-paper))',
          border: 'hsl(var(--kf-line))',
          primary: 'hsl(var(--kf-accent))',
          accent: 'hsl(var(--kf-accent))',
          amber: 'hsl(var(--kf-warning))',
          emerald: 'hsl(var(--kf-success))',
          sky: 'hsl(var(--kf-accent))',
        },
        slate: neutral,
        /* Accent aliases: one brand colour, no second identity */
        blue: accent,
        sky: accent,
        indigo: accent,
        purple: accent,
        violet: accent,
        pink: accent,
        emerald: success,
        green: success,
        amber: warning,
        yellow: warning,
        rose: danger,
        red: danger,
      },
      fontFamily: {
        sans: ['IBM Plex Sans', 'ui-sans-serif', 'system-ui', '-apple-system', 'Segoe UI', 'sans-serif'],
        mono: ['IBM Plex Mono', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
      borderRadius: {
        sm: '0.1875rem',
        DEFAULT: '0.25rem',
        md: '0.375rem',
        lg: '0.5rem',
        xl: '0.625rem',
        '2xl': '0.75rem',
        '3xl': '0.875rem',
        '4xl': '1rem',
      },
      boxShadow: {
        '2xs': '0 1px 1px hsl(var(--kf-ink) / 0.04)',
        xs: '0 1px 2px hsl(var(--kf-ink) / 0.06)',
        card: 'var(--kf-shadow-card)',
        soft: 'var(--kf-shadow-card)',
        elevated: 'var(--kf-shadow-sheet)',
        sheet: 'var(--kf-shadow-sheet)',
      },
      backdropBlur: {
        xs: '2px',
      },
      scale: {
        98: '0.98',
      },
      spacing: {
        13: '3.25rem',
        34: '8.5rem',
      },
    },
  },
  plugins: [],
}
