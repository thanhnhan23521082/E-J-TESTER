# Design System Specification: The Academic Atelier

## 1. Overview & Creative North Star
**Creative North Star: "The Editorial Mentor"**
This design system moves away from the sterile, "boxy" nature of traditional EdTech platforms to embrace a high-end editorial aesthetic. We treat every dashboard and lesson plan as a curated piece of academic literature. By utilizing **intentional asymmetry**, **tonal layering**, and **expansive whitespace**, we create an environment that feels premium, Vietnamese-first, and authoritative yet deeply warm. 

The goal is to break the "grid-lock" of standard SaaS products. We utilize overlapping elements—such as a student's gaming-inspired progress card bleeding slightly over a content section—to create a sense of physical depth and organic flow.

## 2. Color Philosophy & Tonal Depth
Our palette is anchored by **ETEST Red (#BB0016)**, but its power is balanced through sophisticated surface nesting rather than harsh containment.

### The "No-Line" Rule
**Explicit Instruction:** Do not use 1px solid borders (`outline`) for sectioning content. To separate a mentor’s data overview from the sidebar, use a background shift from `surface` (#F9F9FF) to `surface-container-low` (#F0F3FF). Boundaries are felt through tonal transitions, not drawn with lines.

### Surface Hierarchy & Nesting
Treat the UI as a series of stacked, fine-paper sheets. 
- **Base Level:** `surface` (#F9F9FF) for the main application background.
- **Mid Level:** `surface-container-low` (#F0F3FF) for secondary sidebar navigation or parent-view cards.
- **Top Level:** `surface-container-lowest` (#FFFFFF) for primary interactive elements, such as student exam modules.

### The "Glass & Gradient" Rule
To elevate the "ETEST Red" from a standard brand color to a premium signature:
- **CTAs:** Use a subtle linear gradient from `primary` (#BB0016) to `primary-container` (#E42027) at a 135-degree angle. This adds "soul" and prevents the color from looking flat.
- **Floating Elements:** Use Glassmorphism for student "Level Up" notifications. Apply `surface-container-lowest` at 80% opacity with a `20px` backdrop-blur to allow the rich background colors to bleed through softly.

## 3. Typography: The Intellectual Voice
We pair the geometric clarity of **Inter** with the rhythmic, elegant character of **Be Vietnam Pro**.

- **Display & Headlines (Be Vietnam Pro):** Used for large impact moments—student milestones or parent welcome headers. The high x-height and Vietnamese-specific character optimizations ensure the brand feels "native" and prestigious.
- **Titles & Body (Inter):** Used for data-rich mentor views and student tasks. Inter’s legibility at small scales (label-sm: 0.6875rem) ensures that complex academic data remains accessible.
- **Editorial Contrast:** Always pair a `display-md` (2.75rem) headline with a significantly smaller `body-md` (0.875rem) sub-text. This high-contrast scale is what gives the platform its "Editorial" feel.

## 4. Elevation & Depth: Tonal Layering
Traditional EdTech uses shadows to hide poor layout. We use Tonal Layering to celebrate structure.

- **The Layering Principle:** Instead of a shadow, place a `surface-container-lowest` card inside a `surface-container` (#E7EEFE) wrapper. The 2-step jump in value creates a natural, soft "lift."
- **Ambient Shadows:** For high-priority student gaming-profile cards, use an extra-diffused shadow: `box-shadow: 0 12px 32px rgba(187, 0, 22, 0.04)`. Note the tint—the shadow uses a fraction of the primary red, not black, to mimic ambient light hitting a warm surface.
- **The "Ghost Border" Fallback:** If a border is required for accessibility (e.g., input fields), use `outline-variant` (#E7BDB8) at **20% opacity**. Never use a 100% opaque border.

## 5. Components & Interface Patterns

### Buttons (The "Call to Action")
- **Primary:** Height 52px. `primary` gradient. Border-radius 12px (`md`).
- **Secondary:** Height 48px. `secondary-container` (#FAE197) background with `on-secondary-container` (#756326) text. This provides a warm, "gold-standard" feel without competing with the Red.
- **Interaction:** On hover, shift the gradient density rather than just darkening the hex code.

### Dashboard Modules
- **Student Profile:** Gaming-inspired. Use `tertiary` (#0058BE) accents for "XP" or "Level" bars. Incorporate rounded avatars (12px) with a `surface-bright` ring.
- **Parent View:** Jargon-free. Use `secondary` tones and increased `spacing-8` (2rem) between elements to reduce cognitive load.
- **Mentor Data-Grid:** Forbid divider lines. Use alternating row colors (`surface` and `surface-container-low`) and `spacing-4` (1rem) for cell padding to let the data breathe.

### Inputs & Selection
- **Text Inputs:** `surface-container-lowest` background. No border, only a subtle `outline-variant` at 10% opacity.
- **Chips:** Selection chips should use the `primary-fixed` (#FFDAD6) background with `on-primary-fixed` (#410003) text for a sophisticated, soft-red tonal look.

## 6. Do’s and Don'ts

### Do:
- **Do** use `spacing-12` (3rem) and `spacing-16` (4rem) to separate major sections. White space is a luxury feature.
- **Do** use Be Vietnam Pro for all Vietnamese character-heavy headings to ensure perfect diacritic positioning.
- **Do** overlap images or illustrations slightly over their container bounds to break the "web-template" feel.

### Don't:
- **Don't** use 1px solid `#E5E7EB` borders. Use a background color shift instead.
- **Don't** use pure black (#000000) for text. Use `on-surface` (#151C27) for a softer, more premium contrast.
- **Don't** use standard "drop shadows." If an element needs to float, use the Ambient Shadow spec (tinted, high-blur, low-opacity).
- **Don't** clutter the Parent Dashboard. If it isn't a vital "at-a-glance" metric, hide it behind a "View Details" action.