# Design system — "Clean broadsheet"

Clean and sleek: a modern editorial interface. Think a quiet print newspaper re-set for the screen — lots of white,
confident serif headlines, hairline rules, one accent colour. No gradients, no emoji, no glassmorphism.

## Colour tokens (`frontend/app/globals.css`)

| Token | Light | Dark | Use |
|---|---|---|---|
| `--paper` | `#FAF8F4` | `#121212` | page background |
| `--paper-2` | `#F2EFE8` | `#1B1B1B` | panels, chips |
| `--ink` | `#141414` | `#EDEAE4` | headlines, body |
| `--ink-2` | `#55524C` | `#A8A49C` | deks, meta |
| `--rule` | `#D9D4CA` | `#2E2E2E` | hairlines |
| `--accent` | `#B4232A` | `#E0565C` | edition number, Blind Spot label, active states |
| `--accent-soft` | `#F6E3E1` | `#3A1F20` | selected chip bg |

## Type

- **Masthead / headlines:** `Fraunces` (Google Fonts), weights 600–800, slight negative tracking (`-0.02em`). Masthead uses opsz 144.
- **Body / UI:** `Inter`, 400/500/600. Body 17px / 1.6 on reader, 14px UI.
- **Meta / labels:** `Inter` 11–12px, uppercase, `letter-spacing: .12em`.
- Scale: 64 / 44 / 30 / 22 / 17 / 14 / 12.

## Layout

- Max width 1180px, 24px gutters, 12-column grid.
- Reader: masthead (full width, double rule below) → hero (8 cols) + sidebar briefs (4 cols) → 3-column story grid separated by vertical hairlines → End of paper.
- Spacing scale: 4, 8, 12, 16, 24, 32, 48, 72.
- Radius: 2px on buttons/chips (print-like, not pill-shaped), 0 on story blocks.
- Shadows: none, except dropdowns `0 8px 24px rgba(0,0,0,.08)`.

## Components

- **Button primary:** ink background, paper text, 44px high, uppercase 12px label. Hover: accent background.
- **Button ghost:** 1px rule border, ink text.
- **Chip:** paper-2 bg, 1px rule border; selected → accent-soft bg + accent border + accent text.
- **Story block:** section kicker (uppercase accent 11px) → headline (serif) → dek (ink-2) → meta row (source · read min) → actions row (Read original ↗ · Why this? · Skip).
- **Skip:** story fades to 35 % opacity, collapses dek, shows "Skipped — less like this" with Undo.
- **Why this?:** inline expandable line in italic serif with a 2px accent left border.
- **Blind Spot:** boxed with 1px accent border, label "BLIND SPOT — outside your usual reading".
- **End of paper:** full-width centred block, large serif "That's the paper.", sub "You're done for today.", quiz below.

## Motion

Subtle only: 150–200ms ease-out on hovers, 300ms fade for skip, loader types out pipeline steps like a teleprinter.
Respect `prefers-reduced-motion`.

## Voice

Dry, calm, editorial. "Setting your type…", "Today's paper is 11 minutes.", "That's the paper."
