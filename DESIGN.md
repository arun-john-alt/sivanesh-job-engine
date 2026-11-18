---
name: Sivanesh Job Engine Celebration
description: A yellow party poster within the preserved job archive.
colors:
  celebration-ink: "#632731"
  celebration-red: "#ad2d41"
  party-yellow: "#ffdf6c"
  party-blue: "#2852a8"
  party-pink: "#e98295"
  party-cream: "#fff8e5"
  string-brown: "#8a4b27"
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
rounded:
  banner: "16px"
spacing:
  desktop-inline: "24px"
components:
  celebration-banner:
    backgroundColor: "{colors.party-yellow}"
    textColor: "{colors.celebration-ink}"
    rounded: "{rounded.banner}"

---

# Design System: Sivanesh Job Engine Celebration

## Overview

**Creative North Star: "A party for Sivanesh"**

A bright yellow party poster celebrates Sivanesh joining Applied Materials. Burgundy lettering, red emphasis, balloon clusters, hanging flags and scattered paper surround a still announcement. Falling confetti and swaying decorations continue automatically while the banner is visible.

This document governs the celebration component only. The archive retains its purple accent, navigation, cards, typography and theme behavior. Source authority is `site/styles.css`, `site/index.html` and `site/celebration.js`; direction context lives in `docs/design/celebration.md`. Fresh motion review approved the continuous-motion revision using normal and reduced-motion seven-frame filmstrips, five viewport widths and reduced-motion screenshots. Deployment verification is tracked separately.

**Key Characteristics:**

- Yellow poster with burgundy lettering and blue, red and pink party decorations.
- Centered two-line congratulations in locally hosted Archivo Black, followed only by the employer.
- Automatic falling confetti, bobbing balloons and swaying top decorations around a clear text area.
- A complete still scene for reduced motion and without JavaScript.

## Colors

### Primary

Party yellow fills the poster. Burgundy celebration ink anchors the first headline line and employer; celebration red emphasizes Sivanesh's name.

### Secondary

Party blue, celebration red and party pink fill balloons and flags. Cream appears in flags, balloon reflections, confetti and the broad employer underline. Brown defines the hanging string and balloon strings. Confetti draws from red, blue, cream, pink and burgundy.

**The Component Boundary Rule.** These colors govern the celebration only; the archive keeps its incumbent identity.

## Typography

**Display Font:** locally hosted Archivo Black with sans-serif fallback. The font lives in `site/assets/fonts/archivo-black.ttf`; its OFL license and source provenance stay with the asset.

**Employer Font:** the archive's inherited system stack. Display and employer roles use the frontmatter values. The employer has a cream underline (9px thick, 3px offset); ink skipping is disabled.

The heading keeps two explicit lines, "You did it," and "Sivanesh!". Each line prevents wrapping. Applied Materials follows the heading. These are the only visible words within the banner.

## Layout

The banner fills the existing main column with margin (24px 0 12px). Its content is a centered grid with minimum height (560px), padding (130px 24px 80px) and copy width capped at (660px). The headline has bottom margin (30px). Balloons sit at the edges, (18px) inset and (175px) from the top, with width `clamp(135px,18vw,220px)`. The flag strip is (160px) high. Static paper spans the scene.

Between (901px) and (1200px), balloons become (145px) wide, sit at (230px) from the top and extend (34px) beyond each side. The headline is (64px); content keeps its minimum height (560px) and uses inline padding (74px).

At widths up to (700px), content has minimum height (430px), padding (172px 18px 64px) and starts at the top of its grid area. Balloons move above the copy, (52px) from the top, (5px) inset and (80px) wide. Flags become (110px) high and span (190%) width with a left offset of (-45%). Static paper opacity is (.8). The display becomes `clamp(38px,10vw,58px)` with line height (1.12) and bottom margin (26px). Employer becomes (27px) with a (7px) underline. Banner top margin becomes (18px).

At widths up to (380px), display becomes (35px), employer (24px), balloons (70px), content minimum height (420px) and inline padding (14px).

## Elevation & Depth

There are no shadows or outer borders. Overlapping balloon ellipses, small cream reflections and curved strings give the flat SVG scene depth. The announcement sits above decoration and the confetti canvas. Canvas particles skip a rectangle around the copy, expanded horizontally by (18px) and vertically by (12px). Decorations never intercept input. The poster clips decoration at its rounded silhouette.

## Shapes

The banner has rounded corners. Flags use triangles; balloons use tilted ellipses with triangular knots and curved strings. Static paper uses short strokes, circles and outlined four-point stars. Runtime confetti mixes rectangular paper and circles. These are original geometric SVG and canvas shapes, with no new raster assets or employer logo.

## Components

### Celebration banner

The section associates its heading through `aria-labelledby`. Decorative SVG and canvas are hidden from assistive technology. The title and employer exist before JavaScript runs. The banner has no buttons, footer, secondary copy or live status.

Decorative Web Animations API loops alternate indefinitely with `ease-in-out` easing. Four balloons bob from (5px) below to (9px) above baseline and rotate from (-3deg) to (3deg), with durations (2400ms + 330ms per index) and staggered negative delays. Flag groups rotate between (-2.5deg) and (2.5deg), using (1900ms + 180ms per index). Static paper groups drift vertically from (-3px) to (5px) and rotate from (-1deg) to (1deg), using (2700ms + 220ms per index). The heading and employer remain still.

Canvas confetti recirculates continuously, falling at (32-76px per second) with lateral drift and spin. Particle count is (55) below a banner width of (600px), otherwise (105). Canvas resolution caps device pixel ratio at (2). Resize recalculates canvas dimensions and the text exclusion rectangle.

Reduced motion leaves the complete still SVG scene and clears the canvas. Hidden pages and offscreen banners pause all loops and canvas drawing; visibility restores motion when reduced motion is off. Page exit pauses effects and page return resynchronizes them. No audio or third-party animation dependency is used.

The sidecar previews the current banner HTML and scoped CSS, including its decorative SVG and empty canvas. It is a static preview; the runtime animation is implemented in `site/celebration.js`. Archive navigation, inputs and cards are outside this component. Fresh motion review approved the sampled normal, reduced-motion, offscreen and resumed states. Browser sampling found 15 running loops after 7.5 seconds, zero offscreen, 15 on return and zero under reduced motion; canvas pixels followed the same active/still states, with no browser errors. The motion-capture CLI failed its pre-interaction rest gate for both captures, so matched Playwright sampling supplied the evidence. This review does not establish frame-rate smoothness. Deployment verification is tracked separately.

## Do's and Don'ts

### Do:

- Do preserve the archive identity outside the celebration component.
- Do keep the title and employer legible without JavaScript.
- Do keep balloons, flags and paper visible in reduced motion.
- Do pause motion in hidden pages and offscreen banners.
- Do keep falling confetti outside the text exclusion rectangle.

### Don't:

- Don't apply the banner palette or Archivo Black to archive screens.
- Don't add controls or supporting prose to the banner.
- Don't make animation necessary to understand the announcement.
- Don't treat a static preview as proof of live motion or deployment.
