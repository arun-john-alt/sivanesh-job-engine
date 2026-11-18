---
name: Sivanesh Job Engine — Celebration
description: A personal placement announcement within the preserved job archive.
colors:
  celebration-ink: "#202626"
  celebration-orange: "#ec552d"
  headline-orange: "#a93418"
  warm-paper: "#faf8f3"
  footer-paper: "#f0eee7"
  supporting-ink: "#515953"
  border: "#d3d2cb"
  button-hover: "#394540"
  button-label: "#fff"
typography:
  display:
    fontFamily: '"Archivo Black", sans-serif'
    fontSize: "clamp(42px,5.5vw,88px)"
    fontWeight: 400
    lineHeight: 1.04
    letterSpacing: "-.035em"
  title:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
    fontSize: "clamp(26px,2.5vw,36px)"
    fontWeight: 650
    lineHeight: 1.15
    letterSpacing: "-.025em"
  body:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
    fontSize: "16px"
    lineHeight: 1.5
  label:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
    fontSize: "13px"
    fontWeight: 600
    lineHeight: 1.6
rounded:
  banner: "16px"
  replay: "6px"
spacing:
  inline-icon: "10px"
  compact-gap: "18px"
  column-gap: "24px"
  desktop-inset: "44px"
components:
  celebration-banner:
    backgroundColor: "{colors.warm-paper}"
    textColor: "{colors.celebration-ink}"
    rounded: "{rounded.banner}"
  replay:
    backgroundColor: "{colors.celebration-ink}"
    textColor: "{colors.button-label}"
    typography: "{typography.label}"
    rounded: "{rounded.replay}"
    padding: "12px 18px"
  replay-hover:
    backgroundColor: "{colors.button-hover}"
  archive-link:
    textColor: "{colors.celebration-ink}"
---

# Design System: Sivanesh Job Engine — Celebration

## Overview

**Creative North Star: "A well-earned next move"**

A warm, personal placement announcement inside the existing job archive. The congratulations and employer carry the message; an original wafer diagram and rising arrow connect the moment to semiconductor work. This document governs the celebration component only. The archive retains its existing purple accent, navigation, cards, typography and theme behavior.

The north star uses the shipped illustration caption. It describes this component, not a replacement identity for the archive. Source authority is `site/styles.css`, `site/index.html` and `site/celebration.js`; product and direction context live in `PRODUCT.md` and `docs/design/celebration.md`.

**Key Characteristics:**
- Warm paper, dark ink and two distinct orange roles.
- Archivo Black for the two-line congratulations; inherited system type for supporting text.
- Flat surfaces, precise SVG geometry and a finite celebration that settles into stillness.

## Colors

### Primary

Bright celebration orange belongs to the rising arrow, light sweep, text selection and confetti. Burnt headline orange gives the second headline line its emphasis and supplies the keyboard focus outline.

### Neutral

Warm paper contains the announcement. A slightly deeper footer paper separates the archive handoff. Celebration ink anchors the title, employer, replay surface and archive link; supporting ink carries the softer copy. A pale border defines the outer silhouette and footer seam. White labels and a muted green hover surface complete the replay states.

**The Component Boundary Rule.** These colors govern the celebration only; the archive keeps its incumbent identity.

## Typography

**Display Font:** locally hosted Archivo Black, with sans-serif fallback. The font is shipped in `site/assets/fonts/archivo-black.ttf`; its accompanying OFL license and source provenance remain with the asset.

**Body Font:** the archive's inherited system stack. Supporting roles use its normal weight unless frontmatter specifies otherwise.

The display role gives the two-line congratulations its weight. The employer is a distinct title role; supporting prose uses body type. The destination introduction uses normal-weight type (13px / 1.5), while captions and the footer use small supporting type (12px). The label role belongs to replay.

## Layout

The banner fills the existing main column. Desktop content uses two columns (1.8fr / 1fr), with a minimum art column (200px), column gap from frontmatter and top/side/bottom padding (52px / 44px / 44px). Its outer margin is (24px 0 12px). Art is capped at (320px).

At widths up to (1100px), columns become (1.7fr / 1fr) with a minimum art width (145px), gap (18px), padding (40px 30px) and display size `clamp(38px,5.2vw,64px)`.

At widths up to (700px), content becomes a block with padding (32px 24px). Display size becomes `clamp(34px,8.5vw,56px)` with line height (1.08). Body copy becomes (14px), employer (24px), and replay label (12px). The art is positioned right at (116px) wide, its caption disappears, and the footer stacks. Employer width is limited to (65%) to reserve space for geometry. Replay remains at least (48px) high.

At widths up to (380px), content padding is (28px 20px), display (32px), employer (23px), art (90px), and employer width (67%). Preserve the two headline lines and the same reading order at every width.

## Elevation & Depth

The component uses no shadows. Paper tones, the fine border, overlapping wafer and arrow, and the clipped light sweep provide separation. The confetti canvas sits above the content without intercepting input. None of this changes archive elevation rules.

## Shapes

A softly rounded banner contains a smaller rounded replay control. The original SVG uses repeated wafer dies, a notched circular edge, a dotted halo and an upward arrow within a bright disc. It is an illustration, not an employer mark. No new shipping raster assets were added.

## Components

### Celebration banner

Lead with the name and the two-line congratulations, then supporting copy, employer and replay. Keep the art decorative (`aria-hidden`) and retain the heading association. The footer provides the archive handoff, with a fine top border and deeper paper background.

The animation uses one entrance easing family (`cubic-bezier(.16,1,.3,1)`). The headline reveals over (600ms), staggered by (160ms); the wafer settles over (800ms), arrow over (500ms), light sweep over (1800ms), and employer over (450ms). Confetti ends at (4.4s). Reduced motion skips the entire sequence; the static announcement is complete before JavaScript runs. Hidden pages, resize and page exit cancel active motion.

### Replay button

The ink surface and white label identify the action. An inline SVG replay icon precedes the text. Hover changes the surface and lifts the control (2px); active returns it to the baseline and scales it (.98). Background and transform transitions use (120ms ease-out). Focus uses the burnt orange outline (3px) with offset (5px). Reduced motion removes transitions and transforms. Native button behavior supports keyboard activation; replay updates a polite status message.

### Archive handoff

The footer link uses celebration ink with an inline SVG arrow, an underline on hover, the shared visible focus treatment and minimum height (32px desktop / 36px mobile). Preserve its destination at `#archive-start`.

The sidecar previews only these three scoped patterns. Inputs, archive navigation and archive cards exist outside this component and are intentionally not redefined here. Its static previews do not execute the runtime animation.

## Do's and Don'ts

### Do:

- **Do** preserve the archive identity outside the celebration component.
- **Do** keep the name, placement and replay control legible without JavaScript.
- **Do** use burnt orange for the headline emphasis and bright orange for geometry.
- **Do** honor reduced motion and stop active motion when the page is hidden, resized or exited.

### Don't:

- **Don't** apply the banner palette or Archivo Black to archive screens.
- **Don't** treat the original wafer illustration as an Applied Materials logo.
- **Don't** make animation necessary to understand the announcement.
