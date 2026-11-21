# design.md — KimiFun

Direction for every UI decision in this product. Read together with `anti-slop/` (the filter).

## Reading

Reading this as: schoolday chemistry workspace for Indonesian high-school teachers and their students, in a **laboratory notebook** visual language, dial **ENERGY 1 / RHYTHM 2 / MOTION 1**.

- **Audience:** a chemistry teacher between classes, a student on a shared school laptop. They read numbers (volumes, pH, scores) more than prose. Legibility outranks spectacle.
- **Dial reason:** ENERGY 1 because this is a working tool used daily, not a pitch page. RHYTHM 2 because a dashboard needs one lead block per screen and quieter supporting blocks, not eight equal cards. MOTION 1 because measurement should not move while being read; only hover, focus and real state changes animate.

## Identity

The motif is the **lab notebook**: warm paper, graphite ink, hairline rules, monospaced numerals for anything measured, and one reagent colour used the way a lab uses a marker pen — only where attention is required.

This is what stops the UI from being swappable with any other dashboard: the surface is paper, not white glass; data is set in mono, prose in Plex Sans; the accent is a reagent green, not the default SaaS blue.

## Palette

2 cores + 1 accent. Status colours are functional only, never decorative.

| Token | Value (HSL) | Role | Why |
|---|---|---|---|
| `--kf-paper` | `40 24% 97%` | app background | Warm paper separates the workspace from white cards without a gradient; a cool grey reads as "generic admin panel". |
| `--kf-surface` | `0 0% 100%` | cards, sheets | Content sits on true white so the paper tone still means "background". |
| `--kf-ink` | `200 22% 12%` | primary text, dark buttons | Graphite with a 200deg cast ties every neutral to the accent instead of Tailwind's flat blue-slate. |
| `--kf-accent` | `174 58% 27%` | primary actions, active state, links | Verdigris, the colour of oxidised copper acetate: a real lab colour, distinguishable from the AI-default blue/purple, and it carries white text at 6.4:1. |
| `--kf-success` | `152 52% 27%` | attended / passed | Functional. |
| `--kf-warning` | `30 76% 32%` | pending / partial | Functional. |
| `--kf-danger` | `355 64% 38%` | destructive, invalid | Functional, destructive actions only. |

Blue, indigo, purple, sky and pink are **removed** as brand accents. They survive only as aliases of the accent ramp so no component keeps a second identity colour.

## Typography

- **IBM Plex Sans** for UI and prose. Chosen because Plex was commissioned for technical and scientific documentation and stays legible at 12-13px with Indonesian diacritics-free text; it is not the model-default Inter/Geist.
- **IBM Plex Mono** for enrollment codes, formula input, volumes, pH and scores. Reason: tabular measurement should not shift width as digits change, and a mono face marks "this is a reading" the way a lab sheet does.
- Headings use weight and size for hierarchy, never wide-tracked uppercase as decoration. Small caps labels are reserved for section labels inside the nav and are set at 11px/600, not 9px/800.

## Shape, elevation, motion

- Radius scale is small and deliberate: 6px controls, 10px cards, 14px sheets and modals. Nothing is pill-shaped except true tokens (dots, avatars, progress).
- Two elevations only: `card` (1px hairline + 1px shadow) for surfaces, `sheet` for modals and popovers. No element floats without being above something.
- No glow, no gradient backgrounds, no blur except one mobile drawer backdrop.
- Motion is hover/press/transition only (150ms). No looping pulses, no floating, no scroll reveal. `prefers-reduced-motion` removes all of it.
- Theme is fixed light. Reason: used on classroom projectors and shared laptops in daylight; a dark default would hurt the primary reading case. No theme toggle ships, so no half-built dark mode exists.

## Layout rules

- One focal block per screen. On the teacher dashboard that is the class roster and its actions; metrics support it and never lead.
- Navigation groups by job: `Mengajar` (today's work) and `Laboratorium` (simulation and assessment). The current destination is marked by a left rule plus weight, not colour alone.
- Every list view ships empty, loading and error states that name the cause and the next action.

## Copy

Indonesian, second person, specific verbs. No em dashes, no emoji in UI text, no "seamless/powerful/revolusioner", no invented numbers. If a value is unknown it says so.

## Verification log (this pass)

Checked in a real browser against the running app (Vite dev server plus a mock API that returns empty collections), not by reading code:

- **Build:** `npm run build` passes; only the pre-existing chunk-size warning.
- **Routing and errors:** every sidebar destination renders its own page with a single `h1` and zero console errors (teacher and student roles). The duplicated "Analisis siswa" nav item was removed; that view is the second tab inside "Kuis & asesmen".
- **Contrast:** scripted audit walked every text node on every screen (background resolved by climbing ancestors, 4.5:1 body / 3:1 large). Result after the pass: 0 failures. Fixes: `--kf-ink-muted` 32%, `--kf-ink-faint` 40%, `slate-400/500` aliases darkened.
- **Overflow:** measured at 320/360/390/414/768/1024/1280 px. `document.scrollWidth` never exceeded the viewport; the only elements past the edge are the lab stage tabs, which sit in their own horizontal scroller.
- **Token wiring:** every custom class (`bg-accent`, `border-accent-line`, `text-ink-muted`, `shadow-sheet`, `backdrop-blur-xs`) was confirmed to emit CSS. `bg-accent` was initially silently dropped because the accent ramp had no `DEFAULT` key, which made the assistant button invisible; ramps now carry `DEFAULT`.
- **Copy honesty:** no invented scores, percentages, streaks or "AI-powered" claims remain; empty states state the cause and the next action.

Screens reviewed: login, teacher dashboard, class management, module management, assessment, virtual lab, and the teacher dashboard at 390px.
