---
name: Sivanesh Job Engine Celebration
description: A yellow party poster within the preserved job archive.
colors:
  celebration-ink: "#632731"
  celebration-red: "#ad2d41"
  party-yellow: "#ffdf6c"
  footer-yellow: "#fbd25a"
  party-blue: "#2852a8"
  party-pink: "#e98295"
  party-cream: "#fff8e5"
  string-brown: "#8a4b27"
  button-hover: "#862134"
typography:
  display:
    fontFamily: '"Archivo Black", sans-serif'
    fontSize: "clamp(48px,6.2vw,88px)"
    fontWeight: 400
    lineHeight: 1.08
    letterSpacing: "-.035em"
  title:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
    fontSize: "clamp(28px,3vw,38px)"
    fontWeight: 750
    lineHeight: 1.2
    letterSpacing: "-.025em"
  body:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
    fontSize: "15px"
    lineHeight: 1.6
  label:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
    fontSize: "14px"
    fontWeight: 650
rounded:
  banner: "16px"
  replay: "8px"
spacing:
  inline-icon: "10px"
  destination-gap: "8px"
  footer-gap: "16px"
  desktop-inline: "24px"
components:
  celebration-banner:
    backgroundColor: "{colors.party-yellow}"
    textColor: "{colors.celebration-ink}"
    rounded: "{rounded.banner}"
  replay:
    backgroundColor: "{colors.celebration-red}"
    textColor: "{colors.party-cream}"
    typography: "{typography.label}"
    rounded: "{rounded.replay}"
    padding: "13px 22px"
  replay-hover:
    backgroundColor: "{colors.button-hover}"
  archive-link:
    textColor: "{colors.celebration-ink}"
---

# Design System: Sivanesh Job Engine Celebration

## Overview

**Creative North Star: "A party for Sivanesh"**

A bright yellow party poster celebrates Sivanesh joining Applied Materials. Burgundy lettering, red emphasis, balloon clusters, hanging flags and scattered paper make the scene celebratory after the animation stops. The user's feedback rejects a restrained career-announcement treatment for this banner.

This document governs the celebration component only. The archive retains its purple accent, navigation, cards, typography and theme behavior. Source authority is `site/styles.css`, `site/index.html` and `site/celebration.js`; product and direction context live in `PRODUCT.md` and `docs/design/celebration.md`. The fresh desktop/mobile render review returned a ship verdict. Deployment is tracked by the separate celebration-only Pages workflow.

**Key Characteristics:**

- Yellow poster with burgundy lettering and blue, red and pink party decorations.
- Centered two-line congratulations in locally hosted Archivo Black.
- A complete static scene with a finite entrance and replay sequence.

## Colors

### Primary

Party yellow fills the poster; a deeper footer yellow separates the archive handoff. Burgundy celebration ink anchors the first headline line, supporting copy and footer. Celebration red emphasizes Sivanesh's name and fills the replay control.

### Secondary

Party blue and party pink fill balloon and flag shapes. Blue also supplies the keyboard focus outline. Cream appears in flags, balloon reflections, confetti, replay text and the broad employer underline. Brown defines the hanging string and balloon strings. The darker replay hover color keeps the control distinct from the poster.

**The Component Boundary Rule.** These colors govern the celebration only; the archive keeps its incumbent identity.

## Typography

**Display Font:** locally hosted Archivo Black with sans-serif fallback. The font lives in `site/assets/fonts/archivo-black.ttf`; its OFL license and source provenance stay with the asset.

**Body Font:** the archive's inherited system stack. Display and employer roles use the frontmatter values. The destination introduction uses (15px / 1.5), the congratulatory sentence uses the body role, replay uses the label role, and the footer uses (12px). Employer text has a cream underline (9px thick, 3px offset) that crosses behind the letters because ink skipping is disabled.

The heading keeps two explicit lines, "You did it," and "Sivanesh!". Each line prevents wrapping. Preserve the reading order from congratulations through employer to replay.

## Layout

The banner fills the existing main column with margin (24px 0 12px). Its content is a centered grid with minimum height (640px), padding (130px 24px 52px) and copy width capped at (660px). Balloons sit at the edges, (18px) inset and (175px) from the top, with width `clamp(135px,18vw,220px)`. The flag strip is (160px) high. Static paper fills the scene. The footer lays out its sentence and archive link horizontally with padding (18px 28px).

Between (901px) and (1200px), balloons become (145px) wide, sit at (230px) from the top and extend (34px) beyond each side. The headline is (64px); content has minimum height (650px) and inline padding (74px).

At widths up to (700px), content has minimum height (560px), padding (172px 18px 42px) and starts at the top of its grid area. Balloons move above the copy, (52px) from the top, (5px) inset and (80px) wide. Flags become (110px) high and span (190%) width with a left offset of (-45%). Static paper opacity is (.8). The display becomes `clamp(38px,10vw,58px)` with line height (1.12); employer becomes (27px), underline (7px), introduction and body copy (13px). The footer stacks with padding (15px 20px), and its archive target is at least (40px) high. Banner top margin becomes (18px).

At widths up to (380px), display becomes (35px), employer (24px), balloons (70px), content minimum height (550px) and inline padding (14px). The congratulatory sentence is capped at (25ch). Replay retains its minimum height (50px) at all widths.

## Elevation & Depth

There are no shadows or outer borders. Overlapping balloon ellipses, small cream reflections and curved strings give the flat SVG scene depth. The content and footer sit above decorative SVG; the confetti canvas sits above both without intercepting input. The poster clips decorations at its rounded silhouette.

## Shapes

A rounded banner contains a smaller rounded replay button. Flags use triangles; balloons use tilted ellipses with triangular knots and curved strings. Static paper uses short strokes, circles and outlined four-point stars. Runtime confetti mixes rectangles, ribbons and circles. These are original geometric SVG and canvas shapes, with no new raster assets or employer logo.

## Components

### Celebration banner

The section associates its heading through `aria-labelledby`. Decorative SVG and canvas are hidden from assistive technology. Full congratulations, employer and controls exist before JavaScript runs.

Entrance motion uses `cubic-bezier(.16,1,.3,1)`. The first headline line rises and scales over (650ms); the second pops through a small overshoot over (800ms), delayed (180ms). Flags reveal over (700ms). Balloons rise, rotate and settle over (1800ms), with delays beginning at (100ms) and increasing by (90ms). The employer group enters over (500ms), delayed (450ms).

Three confetti volleys launch from the two edges, with staggered delays starting around (.2s), (.75s) and (1.3s). Particle count is (150) below a banner width of (600px), otherwise (260). Canvas resolution caps device pixel ratio at (2). The final fade occupies (.6s); motion clears by (4.8s). Reduced motion leaves the full static scene. Hidden pages, resize, page exit and motion preference changes cancel active effects.

### Replay button

An inline party-popper SVG precedes "Celebrate again". The red surface uses cream text, horizontal padding (22px), vertical padding (13px) and a minimum height (50px). Hover darkens the surface and lifts the control (2px); active returns it to baseline and scales it (.97). Background and transform transitions use (120ms ease-out). Focus uses a blue outline (3px) with offset (5px). Reduced motion removes transitions and transforms. Native button activation updates a polite status with the congratulations before replaying.

### Archive handoff

The deeper yellow footer contains a sentence and underlined archive link with an inline arrow. Hover thickens the underline (2px). The link shares the visible focus treatment and has minimum height (32px desktop / 40px mobile). Preserve its destination at `#archive-start`.

The sidecar previews only these three scoped patterns. Its full-banner preview contains the actual SVG scene and static copy; it does not execute runtime confetti. Archive navigation, inputs and cards are outside this component.

## Do's and Don'ts

### Do:

- Do preserve the archive identity outside the celebration component.
- Do keep the name, placement and replay control legible without JavaScript.
- Do keep balloons, flags and paper visible when the animation stops.
- Do honor reduced motion and cancel active motion on hidden pages, resize and page exit.

### Don't:

- Don't apply the banner palette or Archivo Black to archive screens.
- Don't make animation necessary to understand the announcement.
- Don't treat a static preview as proof of live motion or deployment.
