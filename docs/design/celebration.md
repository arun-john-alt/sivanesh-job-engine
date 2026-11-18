# Placement celebration

Scope: celebration banner only. Mode: Experience. Sivanesh joined Applied Materials; the archive and disabled search workflows are outside the visual change.

## Direction contract

THESIS: A personal celebration that reads as a party even after the animation stops. The user's feedback rejects the restrained career-announcement treatment.

OWN-WORLD: A yellow poster, burgundy Archivo Black lettering, blue and pink balloons, hanging flags and scattered paper. Keep the archive's purple system outside this component.

STORY: The visitor sees Sivanesh's name, understands he joined Applied Materials, without a button or supporting prose in the banner. The archive remains below it.

FIRST VIEWPORT: Centered two-line congratulations with large balloon clusters at the edges, flags across the top, employer below the title, with no controls or secondary copy. On phones the balloons sit above the copy. Confetti falls continuously around a clear text area; balloons, flags and paper sway automatically.

FORM: seed: none (narrow component revision). Code-led revision of the existing banner following the user's explicit request for a more celebratory result. No page-level concept tournament.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance.

## Motion

Playful personality. Focal moment: an ongoing party scene, with falling paper, bobbing balloons and swaying bunting. The headline and employer stay still. There are no replay controls or state changes to explain. Smooth alternate loops use 1.9-3.8 second timings; canvas paper falls at 32-76px per second. The canvas uses 55 particles on phones and 105 on desktop, with a device-pixel-ratio cap of two. Paper does not draw inside the announcement bounds.

Motion starts automatically while the banner is visible. Hidden tabs and offscreen banners pause the canvas and all decorative animation; returning resumes them. Reduced motion displays the complete still scene. Resize updates the canvas bounds and text exclusion area. No audio, flashing or third-party animation dependency.

## Assets

Archivo Black is self-hosted under the OFL license. Source: https://github.com/google/fonts/tree/main/ofl/archivoblack. Flags, balloon ellipses and paper shapes are original geometric SVG and canvas shapes. No new raster assets or third-party runtime dependencies.

## Review

Fresh motion review approved the continuous scene with no material fixes, from normal/reduced seven-frame samples, five width captures, source and supplied browser checks. CLI motion-capture could not pass its pre-interaction rest gate; matched Playwright sampling verified continuity and layout, not frame-rate smoothness. Deployment is tracked separately. The archive and disabled search workflows remain outside this change.
