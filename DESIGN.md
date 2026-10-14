# DESIGN.md — Mincheng Li data portfolio

References: colour and atmosphere from [getuni.co](https://www.getuni.co/); layout, type scale and motion from [screen.movie](https://screen.movie/). Interaction level: **L2**. Stack: static HTML, CSS and vanilla JS for GitHub Pages.

## 1. Visual theme and atmosphere

A light, warm page with coffee-brown text that behaves like screen.movie: everything centred, very large tight headlines, a floating pill nav, and big rounded "windows" that hold the live charts the way that site holds its app screenshots. The colour comes from Uni: a soft, grainy peach, pink and apricot wash with a cool blue edge, and pill buttons.

Keywords: warm, soft light, confident, precise, hands-on.
One line: a sunrise-coloured page where each project is a window you can flip between two answers.

The core idea stays from the previous version: each project has one switch that changes what is counted, and the chart reshapes.

## 2. Colour palette and roles

Approved version: light warm base with deep coffee-brown text (not pure black), Uni's peach, pink and apricot as a soft wash.

```css
:root {
  --page: #fdf9f5;      --page-rgb: 253, 249, 245;    /* page background */
  --surface: #ffffff;   --surface-rgb: 255, 255, 255; /* chart windows, panels, nav */
  --card: #f9f0e8;      --card-rgb: 249, 240, 232;    /* feature and method cards, controls */
  --ink: #2b1a14;       --ink-rgb: 43, 26, 20;        /* text */
  --ink-2: rgba(43, 26, 20, .64);                     /* large secondary text */
  --ink-3: rgba(43, 26, 20, .48);                     /* captions, meta */
  --line: rgba(43, 26, 20, .10);                      /* hairlines, borders */
  --key: #2b1a14;       --on-key: #ffffff;            /* highlighted data marks and their labels */
  --mute: #f3d6c7;                                    /* all other data marks */
  --neg: #d9622f;                                     /* negative values in diverging bars */
  --peach: #f9d5c5;     --peach-rgb: 249, 213, 197;   /* wash */
  --pink: #f7c3ce;      --pink-rgb: 247, 195, 206;    /* wash */
  --apricot: #f6b592;   --apricot-rgb: 246, 181, 146; /* wash, highlight behind key figures */
  --ember: #f2946a;     --ember-rgb: 242, 148, 106;   /* wash hot spot, window glow */
  --sky: #b8cdf2;       --sky-rgb: 184, 205, 242;     /* wash cool edge */
  --amber: #d9622f;     --amber-rgb: 217, 98, 47;     /* focus ring, hand note */
}
```

Roles
- Text is always the coffee ink or its two alphas, except white text on ink fills (primary button, selected switch or filter, key data segment).
- Data: the highlighted or selected entity is `--key`; every other mark is `--mute`; negative values are `--neg`. Gaps between marks are 2px.
- The key figure in each result sentence sits on an `--apricot` highlight.
- The wash appears only in the hero frame, the project page headers, the glow under chart windows and the contact frame. Its centre is lightened so text keeps its contrast.

## 3. Typography

```css
@import url("https://fonts.googleapis.com/css2?family=Inter+Tight:wght@500;600;700&family=Inter:wght@400;500;600&family=Caveat:wght@500&display=swap");
--display: "Inter Tight", "Helvetica Neue", Arial, sans-serif;
--text: "Inter", -apple-system, "Segoe UI", Roboto, sans-serif;
--hand: "Caveat", "Bradley Hand", cursive;
```

| Role | Font | Size (desktop / mobile) | Line | Weight | Tracking |
|---|---|---|---|---|---|
| H1 hero | Inter Tight | 88 / 44 | 1.0 | 700 | -0.045em |
| H2 section | Inter Tight | 60 / 34 | 1.0 | 700 | -0.045em |
| H3 card | Inter Tight | 38 / 26 | 1.05 | 700 | -0.04em |
| Lead (secondary) | Inter Tight | 26 / 19 | 1.2 | 500 | -0.02em, colour `--ink-2` |
| Result sentence | Inter Tight | 28 / 21 | 1.15 | 600 | -0.03em |
| Body | Inter | 17 / 16 | 1.55 | 400 | 0 |
| UI, chips, table | Inter | 14 | 1.3 | 500 | 0 |
| Hand note | Caveat | 24 | 1 | 500 | 0 |

Numbers use `font-variant-numeric: tabular-nums`. Forbidden: serif faces, monospace labels, all-caps tracked eyebrows, gradient-filled text.

Text decoration: headings are solid ink. No gradient or shadow on type; the wash behind the hero already carries the colour.

## 4. Components

**Floating nav.** Fixed, centred pill, 56px tall, radius 999px, `rgba(var(--surface-rgb), .72)` with `backdrop-filter: blur(12px)`, 1px `--line` border. Name at left, four project anchors, black "Email me" pill at right. After 40px of scroll it gains a soft shadow. Mobile: name plus the Email pill only.

**Buttons.** Pill, 52px tall, 17px/600.
- Primary: `--ink` background, white text. Hover: lifts 2px with shadow. Active: returns, scale .98. Focus: 3px `--amber` ring with 3px offset. Disabled: 40% opacity.
- Secondary: white background, ink text, 1px `--line`. Same states.

**Chips.** 32px pill, white at 70% opacity over the wash or `--card` elsewhere, 14px/500, no interaction.

**Window (chart frame).** White surface, radius 28px (20 mobile), 1px `--line`, a title bar with three dots and the project name, shadow `0 40px 80px -40px rgba(var(--apricot-rgb), .55)`. Holds: question, switch, result sentence, chart, values table, footnote.

**Switch.** Two-option pill on `--card`, 44px tall. The selected option is a white pill with a small `--amber` dot that slides between options (transform, 300ms). Hover on the unselected side: text goes from `--ink-2` to `--ink`. Focus ring as buttons.

**Feature card.** `--card` background, radius 28px, window on top, then H3 and lead text, then links. A soft apricot spotlight follows the cursor inside the card (desktop, hover-capable devices only).

**Method card.** Three in a row, `--card`, radius 24px, small icon tile, 20px/600 title, body text. The third is white with a border, like the reference.

**Links.** Ink, 1px underline with 3px offset; hover thickens to 2px.

**Tooltip.** Ink background, white 13px text, radius 8px, follows the pointer.

## 5. Layout

- Content max width 1200px; text blocks max 760px and centred. Side padding 32px (16 mobile).
- Section spacing 160px desktop, 96px mobile. Spacing scale: 4, 8, 12, 16, 24, 32, 48, 64, 96, 160.
- Page order:
  1. Floating nav
  2. Hero inside an inset rounded frame (12px from the viewport edge, radius 24px) filled with the wash: descriptor line, H1, lead, two buttons, chip row
  3. Ontario window, overlapping the bottom of the hero frame
  4. Statement H2 with word-by-word reveal
  5. Three feature cards: Toronto outbreaks, TTC delays, AdventureWorks
  6. "How every project is built": three method cards
  7. Contact frame with the wash, then a plain footer
- Alignment: centred for hero, section headings and statement; left-aligned inside windows and cards.

## 6. Depth and elevation

| Level | Use | Shadow |
|---|---|---|
| 0 | Page, cards | none |
| 1 | Nav after scroll, secondary button hover | `0 8px 24px -12px rgba(var(--ink-rgb), .18)` |
| 2 | Primary button hover | `0 14px 28px -14px rgba(var(--ink-rgb), .45)` |
| 3 | Chart windows | `0 40px 80px -40px rgba(var(--apricot-rgb), .55)` |

A fine grain texture (inline SVG noise, 6% opacity) sits over the wash only.

## 7. Animation and interaction (L2)

Easing `cubic-bezier(.2, .7, .2, 1)`; chart morphs use `cubic-bezier(.6, 0, .2, 1)` at 700ms.

| Category | Effect | Where |
|---|---|---|
| Text, H1 | Words rise and fade in, 60ms stagger, once on load | Hero headline |
| Text, H2 | Words go from 15% to 100% opacity as the heading crosses the viewport | Statement and section headings |
| Text, label | The Caveat note "flip me" draws in with its arrow beside the first switch | Ontario window |
| Element | Buttons lift on hover; switch dot slides | Buttons, switches |
| Component | Cursor spotlight inside feature cards; chart morphs on switch | Cards, windows |
| Background | The wash drifts slowly (40s loop, background-position only) | Hero and contact frames |

Also:
- The Ontario window scales from .94 to 1 and rises as it enters (scroll-linked, transform only).
- Cards and method tiles fade up 24px on entering the viewport, once.
- Each switch flips itself once the first time its window is fully in view, then waits for the reader.
- Nav gains its shadow after 40px of scroll.

Performance rules: no WebGL, no scroll-jacking, no `filter: blur()` on moving elements, pointer listeners throttled with `requestAnimationFrame`, spotlight only under `(hover: hover)`.

`prefers-reduced-motion: reduce`: no entrance, drift, parallax or auto-flip; text is fully visible; switches change state instantly.

## 8. Do's and don'ts

Do
- Keep every figure traceable to a project's own output files.
- Keep the highlighted entity the same colour in both states of a switch.
- State each chart's limit in its footnote.
- Keep the values table under every proportional strip.
- Centre headings; left-align anything that is read as data.

Don't
- Don't put the wash behind body text or charts.
- Don't use a second accent colour or coloured text.
- Don't use dual axes, pie charts or 3D chart effects.
- Don't animate anything that carries a number except in response to a switch.
- Don't use emoji, stock photos or placeholder blocks.
- Don't show a phone number.
- Don't add sections that are not on the resume (testimonials, client logos, pricing).
- Don't let any line of body text exceed 72 characters.

## 9. Responsive behaviour

| Breakpoint | Changes |
|---|---|
| ≥ 1024px | Full layout; feature cards place the window beside or above text; method cards in three columns |
| 640–1023px | Type steps down one size; method cards in one column; nav keeps two anchors |
| < 640px | Hero frame inset 8px; H1 44px; windows radius 20px; ranked bars put the label above the bar; tables keep four columns and scroll inside the window if needed; nav shows name and Email only |

Touch targets are at least 44×44px. No horizontal page scroll at 360px. Keyboard focus is visible on every control; switches are real buttons with `aria-pressed`; result sentences are `aria-live="polite"`.
