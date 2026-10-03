# CycloneGuard Design System & Visual Specification

> **Version**: 1.5.0  
> **Status**: Approved Baseline for Sprint 1.5 & Future Sprints  
> **Design Philosophy**: *"Meteorological Operations Center + Modern Editorial Interface"*

---

## 1. Core Visual Concept & Principles

CycloneGuard is an AI-powered tropical cyclone intelligence platform designed for meteorologists, disaster response commanders, and atmospheric researchers. 

The visual design communicates:
$$\text{DATA} \longrightarrow \text{OBSERVATION} \longrightarrow \text{ANALYSIS} \longrightarrow \text{DECISION}$$
rather than:
$$\text{AI} \longrightarrow \text{MAGIC} \longrightarrow \text{RESULT}$$

### Design Principles:
1. **Light-First Architecture**: Warm, off-white primary backgrounds with charcoal typography for maximum legibility in continuous-monitoring operations centers.
2. **Intentional & Scientific**: No neon glows, no purple/blue generic AI gradients, no gratuitous glassmorphism, and no rounded-2xl bubble cards.
3. **Data as Centerpiece**: The oceanic map canvas, time-series wind velocity curves, and feature attribution overlays are the visual focus.
4. **Calm Precision**: Controlled color accents (deep ocean teal, restrained amber, controlled red, muted green) reserved exclusively for functional and meteorological meaning.
5. **Human-Designed Hierarchy**: Generous whitespace, editorial typography hierarchy, tabular numerals for telemetry, and restrained shape language.

---

## 2. Centralized Color System

All colors across CycloneGuard are strictly governed by centralized CSS variables defined in [`frontend/app/globals.css`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/frontend/app/globals.css). Hardcoding random colors inside individual components is prohibited.

| Token | CSS Variable | Hex Value | Purpose / Meaning |
| :--- | :--- | :--- | :--- |
| **Background** | `--background` | `#f8f9fa` | Warm off-white primary page background |
| **Surface** | `--surface` | `#ffffff` | Pure white card and panel background |
| **Surface Elevated** | `--surface-elevated` | `#ffffff` | Popovers, modals, dropdowns |
| **Surface Muted** | `--surface-muted` | `#f1f3f4` | Table headers, secondary toolbars |
| **Surface Sunken** | `--surface-sunken` | `#eaedef` | Input backgrounds, active tab segments |
| **Foreground** | `--foreground` | `#182026` | Deep charcoal primary typography |
| **Foreground Muted**| `--foreground-muted` | `#5f6b7c` | Secondary labels, captions, metadata |
| **Border** | `--border` | `#e2e6e9` | Subtle structural 1px dividers |
| **Border Focus** | `--border-focus` | `#0f5b6c` | Active input and keyboard focus rings |
| **Brand** | `--brand` | `#0f5b6c` | Deep ocean teal primary accent |
| **Brand Hover** | `--brand-hover` | `#0c4957` | Deep ocean hover state |
| **Brand Subtle** | `--brand-subtle` | `#edf5f7` | Teal tint for badges and highlights |
| **Warning** | `--warning` | `#b45309` | Restrained amber for advisories & watch alerts |
| **Warning Subtle** | `--warning-subtle` | `#fef8ee` | Light amber background tint |
| **Danger** | `--danger` | `#b91c1c` | Controlled red for critical warnings & RI alerts |
| **Danger Subtle** | `--danger-subtle` | `#fef2f2` | Light red background tint |
| **Success** | `--success` | `#1b7a4f` | Muted green for healthy systems & stable states |
| **Success Subtle** | `--success-subtle` | `#f0fdf4` | Light green background tint |
| **Info** | `--info` | `#1f5f7c` | Neutral maritime blue for system telemetry |

---

## 3. Typography Hierarchy

CycloneGuard relies on a clean, professional geometric sans-serif typeface (Inter with system sans-serif fallback) paired with tabular numerals for telemetry values.

| Level | Size / Line Height | Weight | Letter Spacing | CSS / Tailwind | Typical Usage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Display** | 36px / 1.15 | 800 (Bold) | -0.025em | `text-3xl sm:text-4xl font-extrabold tracking-tight` | Landing page hero headline |
| **H1** | 24px / 1.25 | 700 (Bold) | -0.02em | `text-xl sm:text-2xl font-bold tracking-tight` | Portal section headers |
| **H2** | 18px / 1.3 | 600 (Semibold) | -0.01em | `text-lg font-semibold tracking-tight` | Panel titles, modal headers |
| **H3** | 14px / 1.4 | 600 (Semibold) | 0 | `text-sm font-semibold` | Card titles, subsection headers |
| **Body** | 13px / 1.5 | 400 (Regular) | 0 | `text-xs sm:text-[13px] leading-relaxed` | Paragraphs, documentation text |
| **Small / Meta** | 11px / 1.4 | 500 (Medium) | 0.01em | `text-[11px] text-[#5f6b7c]` | Timestamps, metadata, notes |
| **Caption / Overline**| 10px / 1.3 | 600 (Semibold) | 0.08em | `text-[10px] uppercase font-mono tracking-widest` | Section overlines, status categories |
| **Numerical Telemetry**| 24px – 36px | 700 (Bold) | -0.01em | `font-tabular font-bold text-2xl sm:text-3xl` | Vmax (128 km/h), MSLP (964 hPa), Lead time (48h) |

---

## 4. Spacing System

Layouts use an 8-point base grid with half-step increments to guarantee visual breathing room and structured rhythm.

- **4px (`space-1` / `p-1`)**: Micro spacing (badge padding, icon gaps).
- **8px (`space-2` / `p-2`)**: Compact spacing (list row padding, button internal gaps).
- **12px (`space-3` / `p-3`)**: Component spacing (card interior padding, table cell vertical padding).
- **16px (`space-4` / `p-4`)**: Standard spacing (panel padding, grid gap between metrics).
- **24px (`space-6` / `p-6`)**: Section spacing (gap between panels, dashboard module margins).
- **32px (`space-8` / `p-8`)**: Major container padding (empty states, modal interiors).
- **48px (`space-12` / `p-12`)**: Landing page section intervals.
- **64px (`space-16` / `p-16`)**: Editorial hero padding and page dividers.

---

## 5. Border & Shape Language

- **Corner Radius**:
  - `rounded-[3px]` / `rounded-[4px]`: Standard for cards, panels, inputs, buttons, and map frames.
  - `rounded-full`: Reserved **only** for status badges, avatar icons, and pill badges where appropriate.
  - **No `rounded-xl` or `rounded-2xl`** cards.
- **Borders**:
  - Standard 1px solid border (`#e2e6e9`).
  - Interactive hover borders: `#cbd2d6`.
  - Focused inputs: 1.5px solid `#0f5b6c` with subtle focus ring.
  - Inactive / placeholder zones: 1px dashed `#e2e6e9`.

---

## 6. Shadow System

CycloneGuard uses physical contrast, spacing, and subtle 1px borders rather than heavy blur shadows.

- **None (`shadow-none`)**: Tables, nested panels, data rows.
- **Subtle (`shadow-[0_1px_3px_rgba(0,0,0,0.04)]`)**: Cards, metrics, primary panels.
- **Elevated (`shadow-[0_4px_12px_rgba(0,0,0,0.08)]`)**: Modals, dropdown popovers, floating map layer controls.

---

## 7. Component Library Summary

All reusable components are located in [`frontend/components/ui/`](file:///c:/Users/maaz2/OneDrive/Desktop/storm/frontend/components/ui/):

1. **Button** (`Button.tsx`):
   - Variants: `default` (deep ocean teal), `secondary` (charcoal), `outline` (white surface with gray border), `ghost` (text-only hover), `danger` (controlled red).
   - Radius: 3px / 4px. No pill buttons.
2. **Input** (`Input.tsx`):
   - Accessible label, helper text, error messaging, subtle border `#e2e6e9`, focus ring `#0f5b6c`.
3. **Select** (`Select.tsx`):
   - Native select wrapper styled with custom chevron, matching input tokens.
4. **Dropdown** (`Dropdown.tsx`):
   - Accessible action menu popover with click-outside detection and keyboard escape handling.
5. **Badge** (`Badge.tsx`):
   - Variants: `default`, `secondary`, `neutral`, `success`, `warning`, `danger`.
6. **StatusBadge** (`StatusBadge.tsx`):
   - Dot-based operational indicators (`operational`, `standby`, `warning`, `critical`, `disconnected`, `awaiting`).
7. **Alert** (`Alert.tsx`):
   - Semantic banners (`info`, `warning`, `danger`, `success`) with light-tint backgrounds and restrained left border accents.
8. **Card** (`Card.tsx`):
   - Crisp `#ffffff` surface, subtle `#e2e6e9` border, optional header, description, and footer slots.
9. **Panel** (`Panel.tsx`):
   - Operational container with `PanelHeader` (title, subtitle, action slot) and `PanelContent`.
10. **Modal** (`Modal.tsx`):
    - Accessible dialog with lightweight backdrop, header, body, footer, and keyboard ESC listener.
11. **Table** (`Table.tsx`):
    - Muted `#f8f9fa` header row, subtle `#e2e6e9` dividers, tabular numeric alignment.
12. **Tabs** (`Tabs.tsx`):
    - `segmented` (compact sunken toggle) and `underline` (editorial border-bottom indicator).
13. **Tooltip** (`Tooltip.tsx`):
    - Minimal dark popover for scientific acronyms (e.g. CDO, Vmax, MSLP, RI).
14. **Breadcrumb** (`Breadcrumb.tsx`):
    - Operational trail with chevrons for hierarchical navigation.
15. **LoadingState** (`Loading.tsx`):
    - Restrained spinner, skeleton loaders, and `AIProcessingState` with subtle progress bar.
16. **EmptyState** (`EmptyState.tsx`):
    - Contextual, human-designed empty states with icons, status badge, and action buttons.
17. **ErrorState** (`ErrorState.tsx`):
    - Operational error alert with error code badge and retry trigger.
18. **Metric** (`Metric.tsx`):
    - Typography-driven telemetry block (label, big numerical value, unit, trend arrow, description).
19. **SectionHeader** (`SectionHeader.tsx`):
    - Section title, overline category, status badge, and action slots.
20. **DataRow** (`DataRow.tsx`):
    - Clean key-value row for observation and model metadata.
21. **MapContainer** (`MapContainer.tsx`):
    - Visually dominant centerpiece map frame with coordinate overlay, layer toggles, and status badges.

---

## 8. Portal Navigation Systems

### User Portal (Public & Analyst Facing)
- **Concept**: Calm, clear, visual, map-centric.
- **Top Navigation Bar**:
  - Left: Logo icon + `CYCLONEGUARD` (brand teal).
  - Navigation: `Monitor`, `History`, `About`.
  - Right: Operational system status badge (`Active Feed` / `Standby`), Analyst Profile / Sign In.
- **No permanent sidebar** by default; full viewport width is preserved for data visualization.

### Admin Portal (Operations & Engineering Facing)
- **Concept**: Operational, dense, system-oriented, monitoring-focused.
- **Left Sidebar Navigation** (`AdminNav`):
  - Fixed 224px width, `#f8f9fa` background, subtle `#e2e6e9` border.
  - Links: `Dashboard`, `Data Sources`, `Models`, `Predictions`, `Alerts`, `Users`, `System`.
  - Active state: `#0f5b6c` with white text.

---

## 9. Data Visualization & Charts Standards

When plotting cyclone trajectories, wind radii, and rapid intensification probabilities:
1. **Palettes**:
   - Observed Data: Deep Ocean Teal (`#0f5b6c`)
   - Predicted Trajectory: Medium Slate / Navy (`#1f5f7c`)
   - Model Uncertainty Envelope: 15% opacity Teal Tint (`rgba(15, 91, 108, 0.15)`)
   - Warning Threshold: Restrained Amber (`#b45309`)
   - Critical Threshold: Controlled Red (`#b91c1c`)
2. **Chart Types**:
   - Prefer: Line charts, time-series curves, wind barb / vector plots, probability density histograms.
   - Prohibited: Rainbow gradients, 3D pie charts, decorative gauges, neon glowing lines.

---

## 10. Responsive Design Rules

All pages must be verified across standard operational breakpoints:
- **Mobile (`375px` – `390px`)**:
  - Header compresses to brand icon and mobile menu toggle.
  - Multi-column metric grids collapse to 2 columns or stacked 1 column.
  - Tables have horizontal scrolling (`overflow-x-auto`) with sticky headers.
- **Tablet (`768px`)**:
  - Metric cards in 2-column or 4-column layouts.
  - Split views (Map + Telemetry) stack vertically.
- **Desktop (`1024px` – `1440px+`)**:
  - Full editorial layouts, prominent 520px+ map canvas, side-by-side telemetry panels.

---

## 11. Accessibility Compliance

- **Contrast**: All body text achieves at least 4.5:1 contrast against `#f8f9fa` and `#ffffff`.
- **Keyboard Navigation**: Interactive elements include visible focus rings (`ring-1 ring-[#0f5b6c]`).
- **Semantic HTML**: Proper heading hierarchy (`h1` through `h4`), semantic `<main>`, `<nav>`, `<header>`, `<aside>`, `<footer>`.
- **Non-Color Indicators**: Status badges combine color with text and iconography so colorblind operators are not excluded.
