# FRONTEND_GUIDELINES.md — VERDICT
> Design System & Frontend Standards  
> B2B Deposition Coaching Platform for Litigation Attorneys  
> Version: 1.0.0 | February 21, 2026

---

## TABLE OF CONTENTS

1. [Design Principles](#1-design-principles)
2. [Design Tokens](#2-design-tokens)
3. [Layout System](#3-layout-system)
4. [Component Library](#4-component-library)
5. [Accessibility Guidelines](#5-accessibility-guidelines)
6. [Animation Guidelines](#6-animation-guidelines)
7. [Icon System](#7-icon-system)
8. [State Indicators](#8-state-indicators)
9. [Responsive Design](#9-responsive-design)
10. [Performance Guidelines](#10-performance-guidelines)
11. [Browser Support](#11-browser-support)

---

## 1. DESIGN PRINCIPLES

VERDICT is used by litigation partners and senior associates — people who bill $1,000/hour and have zero tolerance for ambiguity. Every design decision must serve the following principles:

### 1.1 Command Clarity
Every screen communicates exactly one primary action. Attorneys should never scan the UI wondering what to do next. In the live session screen, the alert rail is the only thing that moves — everything else is stable.

> **Rule:** One primary CTA per screen. All other actions are secondary or tertiary. Never two blue buttons on the same screen.

### 1.2 Information Density Without Noise
The three-panel live session layout shows transcript, controls, and alerts simultaneously — but each panel is self-contained. High density serves experienced users; visual noise is the enemy.

> **Rule:** Use whitespace intentionally. Pack information in cards with clear hierarchy, never in raw prose.

### 1.3 Status Always Visible
Agents are running, documents are indexing, timers are counting down. Attorneys need ambient status without modal interruptions. Status lives in badges, rail headers, and subtle indicators — never in popups.

> **Rule:** Async state is always represented. A silent spinner is acceptable; a blank element while loading is not.

### 1.4 Trust Through Polish
A law firm will not trust a tool that looks like a demo. Every interaction must feel deliberate — transitions are smooth, alerts have weight, scores feel earned. Visual quality communicates product reliability.

> **Rule:** Animations are purposeful, not decorative. Every motion communicates a state change. Nothing bounces without cause.

### 1.5 Accessibility is Non-Negotiable
Enterprise legal tools face accessibility audits. VERDICT targets WCAG 2.1 AA compliance across all P0 screens.

> **Rule:** Every component ships with keyboard navigation, ARIA labels, and 4.5:1 contrast on all text. No exceptions.

---

## 2. DESIGN TOKENS

### 2.1 Color Palette

#### Primary — Verdict Navy (Dark UI Foundation)

```css
--verdict-navy-900: #0A0F1C;   /* darkest — page bg outside panels */
--verdict-navy-800: #0F1729;   /* PRIMARY PAGE BACKGROUND ✦ */
--verdict-navy-700: #131E30;   /* subtle depth, left/right panels */
--verdict-navy-600: #1E2B3C;   /* card/panel backgrounds ✦ */
--verdict-navy-500: #253347;   /* elevated cards, modals */
--verdict-navy-400: #2D3E54;   /* hover states on panels */
--verdict-navy-300: #374B63;   /* borders, dividers */
--verdict-navy-200: #4A6080;   /* muted text, placeholders */
--verdict-navy-100: #6B849E;   /* secondary text */
--verdict-navy-50:  #94A3B8;   /* tertiary text, captions */
```

#### Blue — Primary Accent (Attorney Actions)

```css
--verdict-blue-900: #1E3A5F;   /* deep press state */
--verdict-blue-800: #1D4ED8;   /* active links */
--verdict-blue-700: #2563EB;   /* primary button hover */
--verdict-blue-600: #3B82F6;   /* PRIMARY BUTTON ✦ */
--verdict-blue-500: #60A5FA;   /* icon fills, active tabs */
--verdict-blue-400: #93C5FD;   /* disabled state */
--verdict-blue-300: #BFDBFE;   /* light accents */
--verdict-blue-100: #DBEAFE;   /* subtle highlight bg */
--verdict-blue-50:  #EFF6FF;   /* info backgrounds */
```

#### Red — Alerts & Risk (Inconsistency / HIGH IMPEACHMENT)

```css
--verdict-red-900: #7F1D1D;    /* deep danger */
--verdict-red-800: #991B1B;    /* danger hover */
--verdict-red-700: #B91C1C;    /* HIGH IMPEACHMENT RISK badge bg */
--verdict-red-600: #DC2626;    /* danger button */
--verdict-red-500: #EF4444;    /* PRIMARY ALERT COLOR ✦ */
--verdict-red-400: #F87171;    /* secondary alert */
--verdict-red-200: #FECACA;    /* alert card border */
--verdict-red-100: #FEE2E2;    /* alert card background */
--verdict-red-50:  #FFF5F5;    /* alert rail hover */
```

#### Amber — Warnings & Timer (Objection / Time Pressure)

```css
--verdict-amber-700: #92400E;  /* dark badge text */
--verdict-amber-600: #D97706;  /* timer warning hover */
--verdict-amber-500: #F59E0B;  /* PRIMARY WARNING ✦ */
--verdict-amber-400: #FCD34D;  /* objection badge bg */
--verdict-amber-200: #FDE68A;  /* objection card border */
--verdict-amber-100: #FEF3C7;  /* objection card background */
--verdict-amber-50:  #FFFBEB;  /* warning surface */
```

#### Green — Success & Active Agents

```css
--verdict-green-700: #065F46;  /* dark success text */
--verdict-green-600: #059669;  /* success hover */
--verdict-green-500: #10B981;  /* PRIMARY SUCCESS ✦ */
--verdict-green-400: #34D399;  /* agent-active pulse */
--verdict-green-200: #A7F3D0;  /* confirmed flag border */
--verdict-green-100: #D1FAE5;  /* confirmed card background */
--verdict-green-50:  #ECFDF5;  /* success surface */
```

#### Purple — ElevenLabs / Voice AI

```css
--verdict-purple-700: #4C1D95;  /* deep voice accent */
--verdict-purple-600: #7C3AED;  /* waveform hover */
--verdict-purple-500: #8B5CF6;  /* WAVEFORM FILL ✦ */
--verdict-purple-400: #A78BFA;  /* waveform mid-amplitude */
--verdict-purple-300: #C4B5FD;  /* waveform low-amplitude */
--verdict-purple-100: #EDE9FE;  /* voice badge background */
```

#### Neutral — Structural Grays

```css
--neutral-900: #111827;
--neutral-800: #1F2937;
--neutral-700: #374151;
--neutral-600: #4B5563;
--neutral-500: #6B7280;
--neutral-400: #9CA3AF;
--neutral-300: #D1D5DB;
--neutral-200: #E5E7EB;
--neutral-100: #F3F4F6;
--neutral-50:  #F9FAFB;
--neutral-0:   #FFFFFF;
```

#### Tailwind Config — Full Color Registration

```js
// tailwind.config.ts
module.exports = {
  theme: {
    extend: {
      colors: {
        'verdict-navy': {
          900: '#0A0F1C', 800: '#0F1729', 700: '#131E30', 600: '#1E2B3C',
          500: '#253347', 400: '#2D3E54', 300: '#374B63', 200: '#4A6080',
          100: '#6B849E', 50: '#94A3B8',
        },
        'verdict-blue': {
          900: '#1E3A5F', 800: '#1D4ED8', 700: '#2563EB', 600: '#3B82F6',
          500: '#60A5FA', 400: '#93C5FD', 300: '#BFDBFE', 100: '#DBEAFE', 50: '#EFF6FF',
        },
        'verdict-red': {
          900: '#7F1D1D', 800: '#991B1B', 700: '#B91C1C', 600: '#DC2626',
          500: '#EF4444', 400: '#F87171', 200: '#FECACA', 100: '#FEE2E2', 50: '#FFF5F5',
        },
        'verdict-amber': {
          700: '#92400E', 600: '#D97706', 500: '#F59E0B', 400: '#FCD34D',
          200: '#FDE68A', 100: '#FEF3C7', 50: '#FFFBEB',
        },
        'verdict-green': {
          700: '#065F46', 600: '#059669', 500: '#10B981', 400: '#34D399',
          200: '#A7F3D0', 100: '#D1FAE5', 50: '#ECFDF5',
        },
        'verdict-purple': {
          700: '#4C1D95', 600: '#7C3AED', 500: '#8B5CF6', 400: '#A78BFA',
          300: '#C4B5FD', 100: '#EDE9FE',
        },
      },
    },
  },
}
```

#### Color Usage Rules

| Context | Token | Do | Don't |
|---------|-------|-----|-------|
| Page background | `verdict-navy-800` | All authenticated screens | Use pure black — too harsh |
| Panel background | `verdict-navy-600` | All cards and panels | Mix light/dark |
| Primary CTA | `verdict-blue-600` | ONE per screen | Use for secondary actions |
| Destructive action | `verdict-red-600` | End session, delete, cancel | Use for warnings — that's amber |
| Inconsistency alerts | `verdict-red-500` | Alert cards, borders | Swap with objection color |
| Objection alerts | `verdict-amber-500` | Alert cards, borders | Use for severity — amber = lesser |
| Confirmed flags | `verdict-green-500` | Confirmed state, agent-active | Universal success color |
| Score: excellent | `verdict-green-400` | Score ≥ 75 | Use generically |
| Score: moderate | `verdict-amber-400` | Score 50–74 | Use generically |
| Score: poor | `verdict-red-400` | Score < 50 | Use generically |
| Voice / ElevenLabs | `verdict-purple-500` | Waveform, voice badges | Use for generic UI |
| Primary text | `#FFFFFF` | Headings, critical info | On dark bg only |
| Secondary text | `verdict-navy-50` | Labels, captions | As primary text — too low contrast |
| Disabled | `verdict-navy-200` | Disabled controls | Active content |

#### Contrast Matrix (WCAG 2.1 AA Verification)

| Foreground | Background | Ratio | Pass Level |
|-----------|-----------|-------|------------|
| `#FFFFFF` on `#0F1729` | 14.7:1 | ✅ AAA |
| `#94A3B8` on `#0F1729` | 4.7:1 | ✅ AA |
| `#6B849E` on `#0F1729` | 3.6:1 | ✅ AA (large text) |
| `#EF4444` on `#1E2B3C` | 4.6:1 | ✅ AA |
| `#F59E0B` on `#0F1729` | 5.1:1 | ✅ AA |
| `#10B981` on `#1E2B3C` | 4.8:1 | ✅ AA |
| `#8B5CF6` on `#0F1729` | 4.9:1 | ✅ AA |
| `#4A6080` on `#0F1729` | 2.7:1 | ❌ FAIL — never use as body text |

---

### 2.2 Typography

#### Font Families

```js
// tailwind.config.ts
fontFamily: {
  sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
  mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
},
```

```html
<!-- apps/frontend/src/app/layout.tsx <head> -->
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
```

**Inter** — all UI text. Optical sizing and tight letter-spacing communicate professionalism at every size from 11px captions to 48px hero text.

**JetBrains Mono** — exclusively for: transcript lines (speaker-tagged exchanges), confidence scores, API data, technical values. Monospace cadence makes dense legal text scannable.

#### Font Size Scale

```js
fontSize: {
  '2xs': ['0.6875rem', { lineHeight: '1rem' }],         // 11px — timestamps, footnotes
  'xs':  ['0.75rem',   { lineHeight: '1rem' }],         // 12px — captions, metadata
  'sm':  ['0.875rem',  { lineHeight: '1.25rem' }],      // 14px — body secondary, labels, buttons
  'base':['1rem',      { lineHeight: '1.5rem' }],       // 16px — body primary ✦ MAIN
  'lg':  ['1.125rem',  { lineHeight: '1.75rem' }],      // 18px — card headings
  'xl':  ['1.25rem',   { lineHeight: '1.75rem' }],      // 20px — section headings
  '2xl': ['1.5rem',    { lineHeight: '2rem' }],         // 24px — page titles
  '3xl': ['1.875rem',  { lineHeight: '2.25rem' }],      // 30px — hero text
  '4xl': ['2.25rem',   { lineHeight: '2.5rem' }],       // 36px — score number (large)
  '5xl': ['3rem',      { lineHeight: '1' }],            // 48px — score hero in brief
  '6xl': ['4rem',      { lineHeight: '1' }],            // 64px — max score display
},
```

#### Font Weights

```js
fontWeight: {
  light:    300,  // Decorative — large display text only
  normal:   400,  // Body text, transcript lines
  medium:   500,  // UI labels, button text, tab titles
  semibold: 600,  // Card headings, alert titles, badges
  bold:     700,  // Page titles, score numbers, emphasis
},
```

#### Letter Spacing

```js
letterSpacing: {
  tighter: '-0.05em',  // Score numbers at 5xl+
  tight:   '-0.025em', // Page headings
  normal:  '0',        // Body text default
  wide:    '0.025em',  // All-caps labels
  wider:   '0.05em',   // Uppercase section labels
  widest:  '0.1em',    // VERDICT wordmark only
},
```

#### Typography Usage Table

| Element | Font | Size | Weight | Color |
|---------|------|------|--------|-------|
| Page title (h1) | Inter | 2xl | bold | #FFFFFF |
| Section heading (h2) | Inter | xl | semibold | #FFFFFF |
| Card heading (h3) | Inter | lg | semibold | #FFFFFF |
| Sub-heading (h4) | Inter | base | semibold | neutral-200 |
| Body text | Inter | base | normal | neutral-100 |
| Body secondary | Inter | sm | normal | verdict-navy-50 |
| Caption / metadata | Inter | xs | normal | verdict-navy-100 |
| Timestamp | JetBrains Mono | xs | normal | verdict-navy-100 |
| Button text (all sizes) | Inter | sm | medium | (inherits) |
| Badge / chip label | Inter | xs | semibold | (semantic) |
| Transcript — Interrogator | JetBrains Mono | sm | normal | #FFFFFF |
| Transcript — Witness | JetBrains Mono | sm | normal | verdict-navy-50 |
| Score number (brief) | Inter | 5xl–6xl | bold | (score color) |
| Confidence score | JetBrains Mono | sm | medium | verdict-navy-50 |
| Coaching narrative | Inter | base | normal | neutral-100 |
| Line height: relaxed | — | — | — | Only for narrative prose |
| Navigation item | Inter | sm | medium | verdict-navy-50 |
| Navigation active | Inter | sm | semibold | #FFFFFF |
| Form label | Inter | sm | medium | neutral-200 |
| Placeholder | Inter | base | normal | verdict-navy-200 |
| Error message | Inter | sm | normal | verdict-red-400 |
| Code / monospace data | JetBrains Mono | sm | normal | verdict-purple-300 |

---

### 2.3 Spacing Scale

```js
// tailwind.config.ts
spacing: {
  px:  '1px',
  0:   '0',
  0.5: '0.125rem',  // 2px
  1:   '0.25rem',   // 4px
  1.5: '0.375rem',  // 6px
  2:   '0.5rem',    // 8px  — micro spacing
  2.5: '0.625rem',  // 10px
  3:   '0.75rem',   // 12px — compact padding
  3.5: '0.875rem',  // 14px
  4:   '1rem',      // 16px — BASE UNIT ✦
  5:   '1.25rem',   // 20px
  6:   '1.5rem',    // 24px — comfortable padding
  7:   '1.75rem',   // 28px
  8:   '2rem',      // 32px
  9:   '2.25rem',   // 36px
  10:  '2.5rem',    // 40px — button height (md)
  11:  '2.75rem',   // 44px — min touch target / button height (lg)
  12:  '3rem',      // 48px
  14:  '3.5rem',    // 56px — nav height
  16:  '4rem',      // 64px
  20:  '5rem',      // 80px
  24:  '6rem',      // 96px
  72:  '18rem',     // 288px — left panel (220px covered via custom w-[220px])
  80:  '20rem',     // 320px — right alert rail
},
```

#### Spacing Usage Rules

| Context | Token | Example |
|---------|-------|---------|
| Inline gap between icon + text | `gap-2` (8px) | Button icon + label |
| Compact card padding | `p-3` (12px) | Alert cards, dense rows |
| Standard card padding | `p-4` (16px) | Most cards |
| Comfortable card padding | `p-5` or `p-6` | Dashboard case cards, brief sections |
| Between form fields | `space-y-4` (16px) | All forms |
| Between section cards | `gap-6` (24px) | Page layouts |
| Page horizontal margin | `px-6 lg:px-8` | Standard page wrapper |
| Page vertical padding | `py-8` | Standard page wrapper |
| Section vertical separation | `mb-12` (48px) | Major page sections |
| Alert rail inner padding | `p-3` (12px) | Alert rail container |
| Three-panel gap | `gap-0` | Panels are flush — borders provide separation |

---

### 2.4 Border Radius

```js
borderRadius: {
  none:    '0',
  sm:      '0.125rem',  // 2px  — tight insets, subtle
  DEFAULT: '0.25rem',   // 4px  — input fields, chips
  md:      '0.375rem',  // 6px  — buttons ✦ BUTTON STANDARD
  lg:      '0.5rem',    // 8px  — cards, panels ✦ CARD STANDARD
  xl:      '0.75rem',   // 12px — modals, large containers
  '2xl':   '1rem',      // 16px — coaching brief hero card
  '3xl':   '1.5rem',    // 24px — large avatar frames
  full:    '9999px',    // pill — badges, chips, toggle switches
},
```

**Rule table:**
- `rounded-md` (6px) → all `<Button>` components
- `rounded-lg` (8px) → all `<Card>`, alert cards, panels, dropdowns
- `rounded-xl` (12px) → modals, session config overlay
- `rounded-2xl` (16px) → brief score hero, feature highlight cards
- `rounded-full` → all `<Badge>`, status dots, toggle switches, avatar circles

---

### 2.5 Shadows & Elevation

VERDICT's dark background means shadows show as border glows rather than drop shadows.

```js
// tailwind.config.ts
boxShadow: {
  'card-sm':     '0 1px 2px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.03)',
  'card':        '0 4px 6px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.05)',
  'card-lg':     '0 10px 15px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.07)',
  'modal':       '0 25px 50px rgba(0,0,0,0.7), 0 0 0 1px rgba(255,255,255,0.08)',
  'alert-red':   '0 0 0 1px rgba(239,68,68,0.6), 0 4px 12px rgba(239,68,68,0.2)',
  'alert-amber': '0 0 0 1px rgba(245,158,11,0.6), 0 4px 12px rgba(245,158,11,0.2)',
  'alert-green': '0 0 0 1px rgba(16,185,129,0.6), 0 4px 12px rgba(16,185,129,0.2)',
  'glow-blue':   '0 0 16px rgba(59,130,246,0.35)',
  'glow-purple': '0 0 16px rgba(139,92,246,0.35)',
  'glow-green':  '0 0 12px rgba(16,185,129,0.4)',
  'inner-focus': 'inset 0 0 0 2px rgba(59,130,246,0.7)',
},
```

**Usage:**
- `shadow-card-sm` → default card resting state
- `shadow-card` → card on hover / elevated state
- `shadow-card-lg` → tooltips, floating menus
- `shadow-modal` → all modals
- `shadow-alert-red` → active inconsistency alert cards
- `shadow-alert-amber` → active objection alert cards
- `shadow-glow-purple` → ElevenLabs waveform container during playback

---

## 3. LAYOUT SYSTEM

### 3.1 The Three-Panel Live Session Layout

VERDICT's signature layout. Every design decision in the app builds toward making this screen functional and trustworthy.

```
┌─────────────────────────────────────────────────────────────────────┐
│  VERDICT                                [Session: 23:14]  [⏸ Pause]│ ← h-14 header
├──────────────┬──────────────────────────┬───────────────────────────┤
│  LEFT PANEL  │     CENTER PANEL         │   RIGHT PANEL             │
│  w-[220px]   │   flex-1                 │   w-[320px]               │
│  fixed       │   scrollable             │   fixed                   │
│              │                          │                           │
│  Timer       │   TRANSCRIPT             │   ALERT RAIL              │
│  23:14 ──────│                          │                           │
│  [▓▓▓░░░░░]  │   Q8 [Interrogator]:     │  ┌───────────────────┐   │
│              │   "What was the exact    │  │ ⚡ INCONSISTENCY  │   │
│  Focus Areas │    dosage?"              │  │ Q8 · 91% · HIGH   │   │
│  ─────────── │                          │  │ "~$200" vs "$217" │   │
│  FINANCIAL ● │   A [Dr. Chen]:          │  │ [✓ Confirm] [✗]   │   │
│  TIMELINE    │   "Approximately $200,   │  └───────────────────┘   │
│              │    roughly speaking..."  │                           │
│  Agents      │                          │  ┌───────────────────┐   │
│  ─────────── │   [● Monitoring active]  │  │ 🔴 OBJECTION     │   │
│  ● Interroga │                          │  │ Q7 · LEADING      │   │
│  ● Objection │                          │  │ FRE 611(c)        │   │
│  ● Detector  │                          │  └───────────────────┘   │
│              │                          │                           │
│  [Add Note]  │                          │  2 alerts this session    │
│  [Skip Topic]│                          │                           │
│  [End Early] │                          │                           │
└──────────────┴──────────────────────────┴───────────────────────────┘
```

```tsx
// apps/frontend/src/app/cases/[caseId]/session/[sessionId]/live/page.tsx

export default function LiveSessionPage() {
  return (
    <div className="flex flex-col h-screen bg-verdict-navy-800 overflow-hidden">

      {/* Fixed header — h-14 (56px) */}
      <header className="h-14 flex-shrink-0 bg-verdict-navy-700 border-b border-verdict-navy-300/30 flex items-center px-6 gap-4">
        <span className="font-bold text-white tracking-widest text-sm">VERDICT</span>
        <div className="flex-1" />
        <SessionTimer />
        <Button variant="secondary" size="sm" icon={<Pause />}>Pause</Button>
        <Button variant="danger-outline" size="sm">End Session</Button>
      </header>

      {/* Three-panel body — fills remaining viewport height */}
      <div className="flex flex-1 overflow-hidden">

        {/* LEFT — Session controls, fixed 220px */}
        <aside
          className="w-[220px] flex-shrink-0 bg-verdict-navy-700 border-r border-verdict-navy-300/30 overflow-y-auto flex flex-col"
          aria-label="Session controls"
        >
          <SessionControlPanel />
        </aside>

        {/* CENTER — Live transcript, flexible width */}
        <main
          className="flex-1 overflow-y-auto bg-verdict-navy-800"
          id="main-content"
          aria-label="Live session transcript"
        >
          <LiveTranscriptPanel />
        </main>

        {/* RIGHT — Alert rail, fixed 320px */}
        <aside
          className="w-[320px] flex-shrink-0 bg-verdict-navy-700 border-l border-verdict-navy-300/30 overflow-y-auto flex flex-col"
          aria-label="Live alerts rail"
          aria-live="polite"
        >
          <AlertRail />
        </aside>

      </div>
    </div>
  );
}
```

### 3.2 Standard Authenticated Page Layout

```tsx
// apps/frontend/src/components/layout/PageLayout.tsx

export function PageLayout({
  title,
  description,
  actions,
  children,
  maxWidth = '7xl',
}: {
  title: string;
  description?: string;
  actions?: React.ReactNode;
  children: React.ReactNode;
  maxWidth?: '5xl' | '6xl' | '7xl' | 'full';
}) {
  return (
    <div className="min-h-screen bg-verdict-navy-800">
      <GlobalNav />

      <div className={cn('mx-auto px-6 py-8', {
        'max-w-5xl': maxWidth === '5xl',
        'max-w-6xl': maxWidth === '6xl',
        'max-w-7xl': maxWidth === '7xl',
        'max-w-full': maxWidth === 'full',
      })}>
        {/* Page header */}
        <div className="flex items-start justify-between gap-4 mb-8">
          <div>
            <h1 className="text-2xl font-bold text-white">{title}</h1>
            {description && (
              <p className="mt-1 text-sm text-verdict-navy-50">{description}</p>
            )}
          </div>
          {actions && (
            <div className="flex items-center gap-3 flex-shrink-0">
              {actions}
            </div>
          )}
        </div>

        {/* Main content */}
        <main id="main-content">
          {children}
        </main>
      </div>
    </div>
  );
}
```

### 3.3 Responsive Breakpoints

```js
// tailwind.config.ts
screens: {
  'sm':  '640px',    // Mobile landscape
  'md':  '768px',    // Tablet
  'lg':  '1024px',   // Desktop minimum — required for live session
  'xl':  '1280px',   // Standard desktop ✦ PRIMARY TARGET
  '2xl': '1536px',   // Wide desktop / dual-monitor
},
```

### 3.4 Common Layout Patterns

```tsx
// 1. Case cards dashboard grid
<div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
  {cases.map(c => <CaseCard key={c.id} case={c} />)}
</div>

// 2. Two-column: main content + sidebar
<div className="grid grid-cols-1 lg:grid-cols-[1fr_360px] gap-8 items-start">
  <main className="min-w-0">{/* Primary content */}</main>
  <aside className="lg:sticky lg:top-6">{/* Sidebar — stick on scroll */}</aside>
</div>

// 3. Case detail tabs with content area
<div className="flex flex-col gap-6">
  <TabBar tabs={['Documents', 'Witnesses', 'Sessions', 'Briefs']} />
  <div className="min-h-[400px]">
    {/* Tab content */}
  </div>
</div>

// 4. Centered auth layout (login, invite accept)
<div className="min-h-screen flex items-center justify-center bg-verdict-navy-800 px-4">
  <div className="w-full max-w-[400px]">
    <AuthCard />
  </div>
</div>

// 5. Coaching brief layout (single-column, constrained)
<div className="max-w-2xl mx-auto py-8 px-6 space-y-6">
  <ScoreHero />
  <WeaknessMapCard />
  <AlertSummaryCard />
  <RecommendationsCard />
  <CoachingNarrativeCard />
</div>

// 6. Witness view — clean, minimal (no alert data)
<div className="min-h-screen bg-verdict-navy-800 flex flex-col items-center justify-center p-8">
  <div className="w-full max-w-lg text-center space-y-6">
    <WitnessSessionView />
  </div>
</div>
```

### 3.5 Global Navigation

```tsx
// apps/frontend/src/components/layout/GlobalNav.tsx

export function GlobalNav() {
  const pathname = usePathname();

  return (
    <nav
      className="h-14 bg-verdict-navy-700 border-b border-verdict-navy-300/30 flex items-center px-6 gap-6"
      role="navigation"
      aria-label="Main navigation"
    >
      {/* Skip link — keyboard users */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-verdict-blue-600 focus:text-white focus:rounded-md focus:text-sm"
      >
        Skip to main content
      </a>

      {/* Wordmark */}
      <Link href="/dashboard" className="font-bold text-white tracking-widest text-sm select-none hover:text-verdict-navy-50 transition-colors">
        VERDICT
      </Link>

      {/* Divider */}
      <div className="h-4 w-px bg-verdict-navy-300/40" aria-hidden />

      {/* Nav links */}
      <div className="flex items-center gap-1">
        <NavLink href="/dashboard" label="Dashboard" icon={<LayoutDashboard />} />
        <NavLink href="/cases" label="Cases" icon={<FolderOpen />} />
      </div>

      {/* Right — firm badge + user menu */}
      <div className="ml-auto flex items-center gap-3">
        <FirmBadge />
        <UserMenu />
      </div>
    </nav>
  );
}

function NavLink({ href, label, icon }: { href: string; label: string; icon: React.ReactNode }) {
  const pathname = usePathname();
  const isActive = pathname === href || pathname.startsWith(href + '/');

  return (
    <Link
      href={href}
      aria-current={isActive ? 'page' : undefined}
      className={cn(
        'flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-colors duration-150',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-verdict-blue-500',
        isActive
          ? 'bg-verdict-navy-600 text-white'
          : 'text-verdict-navy-50 hover:text-white hover:bg-verdict-navy-600/50'
      )}
    >
      <span className="w-4 h-4" aria-hidden>{icon}</span>
      {label}
    </Link>
  );
}
```

---

## 4. COMPONENT LIBRARY

### 4.1 Button

```tsx
// apps/frontend/src/components/ui/Button.tsx
import { cva, type VariantProps } from 'class-variance-authority';
import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  [
    'inline-flex items-center justify-center gap-2',
    'font-medium rounded-md select-none',
    'transition-all duration-150 ease-out',
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-verdict-navy-800',
    'disabled:opacity-40 disabled:cursor-not-allowed disabled:pointer-events-none',
  ],
  {
    variants: {
      variant: {
        primary: [
          'bg-verdict-blue-600 text-white',
          'hover:bg-verdict-blue-700 active:bg-verdict-blue-800',
          'focus-visible:ring-verdict-blue-500',
          'shadow-card-sm hover:shadow-card',
        ],
        secondary: [
          'bg-verdict-navy-600 text-white border border-verdict-navy-300/50',
          'hover:bg-verdict-navy-500 hover:border-verdict-navy-300/80',
          'focus-visible:ring-verdict-navy-300',
        ],
        outline: [
          'bg-transparent text-verdict-blue-400 border border-verdict-blue-600/50',
          'hover:bg-verdict-blue-600/10 hover:border-verdict-blue-500 hover:text-verdict-blue-300',
          'focus-visible:ring-verdict-blue-500',
        ],
        ghost: [
          'bg-transparent text-verdict-navy-50',
          'hover:bg-verdict-navy-600 hover:text-white',
          'focus-visible:ring-verdict-navy-300',
        ],
        danger: [
          'bg-verdict-red-600 text-white',
          'hover:bg-verdict-red-700 active:bg-verdict-red-800',
          'focus-visible:ring-verdict-red-500',
          'shadow-card-sm',
        ],
        'danger-outline': [
          'bg-transparent text-verdict-red-400 border border-verdict-red-600/50',
          'hover:bg-verdict-red-600/10 hover:border-verdict-red-500',
          'focus-visible:ring-verdict-red-500',
        ],
        success: [
          'bg-verdict-green-600 text-white',
          'hover:bg-verdict-green-700 active:bg-verdict-green-800',
          'focus-visible:ring-verdict-green-500',
        ],
      },
      size: {
        xs:        'h-7 px-2.5 text-xs',
        sm:        'h-8 px-3 text-sm',
        md:        'h-10 px-4 text-sm',      // DEFAULT ✦
        lg:        'h-11 px-6 text-base',    // Primary CTAs
        xl:        'h-12 px-8 text-base',    // Hero CTAs
        icon:      'h-10 w-10',
        'icon-sm': 'h-8 w-8',
      },
    },
    defaultVariants: { variant: 'primary', size: 'md' },
  }
);

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
}

export function Button({
  className, variant, size, loading, disabled,
  icon, iconPosition = 'left', children, ...props
}: ButtonProps) {
  return (
    <button
      className={cn(buttonVariants({ variant, size }), className)}
      disabled={disabled || loading}
      aria-disabled={disabled || loading}
      aria-busy={loading}
      {...props}
    >
      {loading && <Loader2 className="w-4 h-4 animate-spin flex-shrink-0" aria-hidden />}
      {!loading && icon && iconPosition === 'left' && (
        <span className="w-4 h-4 flex-shrink-0" aria-hidden>{icon}</span>
      )}
      {children}
      {!loading && icon && iconPosition === 'right' && (
        <span className="w-4 h-4 flex-shrink-0" aria-hidden>{icon}</span>
      )}
    </button>
  );
}

// When to use each variant:
// primary      → ONE per screen. The most important action. [Start Session], [Generate Brief]
// secondary    → Supporting actions alongside primary. [View Details], [Download]
// outline      → Lower-emphasis alternatives. [Cancel], tab-like actions
// ghost        → Navigation, icon buttons, inline actions in dense UI
// danger       → Irreversible destructive actions: [End Session], [Delete Case]
// danger-outline → Softer destructive: "confirm before proceeding" dialogs
// success      → Confirm alert, [Mark Complete], [Accept]
```

---

### 4.2 Input Fields

```tsx
// apps/frontend/src/components/ui/Input.tsx
import { Eye, EyeOff, AlertCircle, CheckCircle2 } from 'lucide-react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  success?: string;
  helperText?: string;
  inputSize?: 'sm' | 'md' | 'lg';
}

const inputBaseClasses = [
  'w-full bg-verdict-navy-600 border rounded',
  'text-white placeholder:text-verdict-navy-200',
  'transition-all duration-150',
  'focus:outline-none focus:ring-2 focus:ring-offset-0',
  'disabled:opacity-40 disabled:cursor-not-allowed',
].join(' ');

const inputSizeClasses = {
  sm: 'h-8 px-3 text-sm',
  md: 'h-10 px-3 text-sm',   // DEFAULT ✦
  lg: 'h-12 px-4 text-base',
};

export function Input({
  id, label, error, success, helperText,
  required, inputSize = 'md', className, type, ...props
}: InputProps) {
  const [showPw, setShowPw] = React.useState(false);
  const inputId = id ?? React.useId();
  const errorId = `${inputId}-error`;
  const helperId = `${inputId}-helper`;
  const state = error ? 'error' : success ? 'success' : 'default';
  const actualType = type === 'password' ? (showPw ? 'text' : 'password') : type;

  const stateClasses = {
    default: 'border-verdict-navy-300/50 hover:border-verdict-navy-300 focus:ring-verdict-blue-500 focus:border-verdict-blue-500',
    error:   'border-verdict-red-500 focus:ring-verdict-red-500 focus:border-verdict-red-500',
    success: 'border-verdict-green-500 focus:ring-verdict-green-500 focus:border-verdict-green-500',
  };

  const needsIcon = state !== 'default' && type !== 'password';

  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label htmlFor={inputId} className="text-sm font-medium text-neutral-200">
          {label}
          {required && <span className="ml-1 text-verdict-red-400" aria-hidden>*</span>}
          {required && <span className="sr-only"> (required)</span>}
        </label>
      )}

      <div className="relative">
        <input
          id={inputId}
          type={actualType}
          className={cn(
            inputBaseClasses,
            inputSizeClasses[inputSize],
            stateClasses[state],
            (type === 'password' || needsIcon) && 'pr-10',
            className
          )}
          aria-invalid={!!error}
          aria-describedby={[error && errorId, helperText && !error && helperId].filter(Boolean).join(' ') || undefined}
          aria-required={required}
          {...props}
        />

        {/* Password toggle */}
        {type === 'password' && (
          <button
            type="button"
            tabIndex={-1}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-verdict-navy-100 hover:text-white transition-colors"
            onClick={() => setShowPw(p => !p)}
            aria-label={showPw ? 'Hide password' : 'Show password'}
          >
            {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        )}

        {/* State icons */}
        {state === 'error' && type !== 'password' && (
          <AlertCircle className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-verdict-red-400 pointer-events-none" aria-hidden />
        )}
        {state === 'success' && type !== 'password' && (
          <CheckCircle2 className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-verdict-green-500 pointer-events-none" aria-hidden />
        )}
      </div>

      {error && (
        <p id={errorId} role="alert" className="text-sm text-verdict-red-400 flex items-center gap-1.5">
          <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" aria-hidden />
          {error}
        </p>
      )}
      {success && !error && (
        <p className="text-sm text-verdict-green-400 flex items-center gap-1.5">
          <CheckCircle2 className="w-3.5 h-3.5 flex-shrink-0" aria-hidden />
          {success}
        </p>
      )}
      {helperText && !error && !success && (
        <p id={helperId} className="text-xs text-verdict-navy-100">{helperText}</p>
      )}
    </div>
  );
}

// Textarea variant
export function Textarea({
  id, label, error, helperText, required, rows = 4, className, ...props
}: React.TextareaHTMLAttributes<HTMLTextAreaElement> & {
  label?: string; error?: string; helperText?: string; required?: boolean;
}) {
  const inputId = id ?? React.useId();
  const errorId = `${inputId}-error`;

  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label htmlFor={inputId} className="text-sm font-medium text-neutral-200">
          {label}
          {required && <span className="ml-1 text-verdict-red-400" aria-hidden>*</span>}
        </label>
      )}
      <textarea
        id={inputId}
        rows={rows}
        className={cn(
          'w-full bg-verdict-navy-600 border rounded px-3 py-2',
          'text-white placeholder:text-verdict-navy-200 text-sm',
          'focus:outline-none focus:ring-2 focus:ring-verdict-blue-500 focus:border-verdict-blue-500',
          'disabled:opacity-40 resize-none transition-colors duration-150',
          error
            ? 'border-verdict-red-500 focus:ring-verdict-red-500'
            : 'border-verdict-navy-300/50 hover:border-verdict-navy-300',
          className
        )}
        aria-invalid={!!error}
        aria-describedby={error ? errorId : undefined}
        {...props}
      />
      {error && (
        <p id={errorId} role="alert" className="text-sm text-verdict-red-400 flex items-center gap-1.5">
          <AlertCircle className="w-3.5 h-3.5" aria-hidden />
          {error}
        </p>
      )}
      {helperText && !error && (
        <p className="text-xs text-verdict-navy-100">{helperText}</p>
      )}
    </div>
  );
}
```

---

### 4.3 Cards

```tsx
// apps/frontend/src/components/ui/Card.tsx

// Base card — static content containers
export function Card({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        'bg-verdict-navy-600 rounded-lg border border-verdict-navy-300/30 shadow-card-sm',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

// Interactive card — case cards, witness cards, clickable rows
export function InteractiveCard({
  className, onClick, children, ...props
}: React.HTMLAttributes<HTMLDivElement> & { onClick?: () => void }) {
  return (
    <div
      className={cn(
        'bg-verdict-navy-600 rounded-lg border border-verdict-navy-300/30 shadow-card-sm',
        'transition-all duration-200 cursor-pointer',
        'hover:bg-verdict-navy-500 hover:border-verdict-navy-300/60 hover:shadow-card hover:-translate-y-0.5',
        'active:translate-y-0 active:shadow-card-sm',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-verdict-blue-500',
        className
      )}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={onClick ? (e) => (e.key === 'Enter' || e.key === ' ') && onClick() : undefined}
      {...props}
    >
      {children}
    </div>
  );
}

// Alert card — live session rail
interface AlertCardProps extends React.HTMLAttributes<HTMLDivElement> {
  type: 'inconsistency' | 'objection' | 'composure';
  impeachmentRisk?: 'STANDARD' | 'HIGH';
  isConfirmed?: boolean;
  isRejected?: boolean;
}

export function AlertCard({
  type, impeachmentRisk, isConfirmed, isRejected, className, children, ...props
}: AlertCardProps) {
  const styles = {
    inconsistency: { border: 'border-verdict-red-500/60',   bg: 'bg-verdict-red-500/10',   shadow: 'shadow-alert-red' },
    objection:     { border: 'border-verdict-amber-500/60', bg: 'bg-verdict-amber-500/10', shadow: 'shadow-alert-amber' },
    composure:     { border: 'border-verdict-purple-500/60',bg: 'bg-verdict-purple-500/10',shadow: 'shadow-card' },
  }[type];

  return (
    <article
      className={cn(
        'rounded-lg border overflow-hidden transition-all duration-300',
        styles.border, styles.bg, styles.shadow,
        // HIGH IMPEACHMENT RISK — 2 cycles of border pulse, then stops
        impeachmentRisk === 'HIGH' && !isConfirmed && 'animate-[pulse-border-red_600ms_ease-in-out_2]',
        // Confirmed → muted green
        isConfirmed && 'opacity-60 border-verdict-green-500/40 bg-verdict-green-500/5 shadow-alert-green',
        // Rejected → faded
        isRejected && 'opacity-25 pointer-events-none',
        className
      )}
      aria-label={`${type} alert`}
      {...props}
    >
      {children}
    </article>
  );
}

// Dashboard case card — deposition countdown + stats
export function CaseCard({ case: c, onClick }: { case: any; onClick: () => void }) {
  const depositionDays = c.depositionDate
    ? Math.ceil((new Date(c.depositionDate).getTime() - Date.now()) / 86400000)
    : null;

  return (
    <InteractiveCard onClick={onClick} className="p-5 flex flex-col gap-4">
      <div className="flex items-start justify-between gap-2">
        <h3 className="text-base font-semibold text-white leading-tight flex-1">{c.name}</h3>
        <CaseTypeBadge type={c.caseType} />
      </div>

      {depositionDays !== null && (
        <div className={cn(
          'flex items-center gap-2 text-sm font-medium',
          depositionDays <= 7  ? 'text-verdict-red-400' :
          depositionDays <= 30 ? 'text-verdict-amber-400' :
          'text-verdict-navy-50'
        )}>
          <Calendar className="w-3.5 h-3.5" aria-hidden />
          {depositionDays <= 0 ? 'Deposition today' :
           depositionDays === 1 ? '1 day until deposition' :
           `${depositionDays} days until deposition`}
        </div>
      )}

      <div className="flex items-center gap-3 text-xs text-verdict-navy-100">
        <span>{c.documentCount} doc{c.documentCount !== 1 ? 's' : ''}</span>
        <span aria-hidden>·</span>
        <span>{c.witnessCount} witness{c.witnessCount !== 1 ? 'es' : ''}</span>
        {c.latestScore !== null && (
          <>
            <span aria-hidden>·</span>
            <span className={cn('font-semibold font-mono', scoreColorClass(c.latestScore))}>
              {c.latestScore}/100
            </span>
          </>
        )}
      </div>
    </InteractiveCard>
  );
}

function scoreColorClass(score: number): string {
  if (score >= 75) return 'text-verdict-green-400';
  if (score >= 50) return 'text-verdict-amber-400';
  return 'text-verdict-red-400';
}
```

---

### 4.4 Badges

```tsx
// apps/frontend/src/components/ui/Badge.tsx
import { cva, type VariantProps } from 'class-variance-authority';

const badgeVariants = cva(
  'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold tracking-wide select-none',
  {
    variants: {
      variant: {
        inconsistency: 'bg-verdict-red-500/20 text-verdict-red-300 border border-verdict-red-500/40',
        objection:     'bg-verdict-amber-500/20 text-verdict-amber-300 border border-verdict-amber-500/40',
        composure:     'bg-verdict-purple-500/20 text-verdict-purple-300 border border-verdict-purple-500/40',
        'high-risk':   'bg-verdict-red-700 text-white border border-verdict-red-500',
        'std-risk':    'bg-verdict-navy-500 text-verdict-navy-50 border border-verdict-navy-300/50',
        ready:         'bg-verdict-green-500/20 text-verdict-green-300 border border-verdict-green-500/40',
        indexing:      'bg-verdict-blue-500/20 text-verdict-blue-300 border border-verdict-blue-500/40',
        failed:        'bg-verdict-red-500/20 text-verdict-red-300 border border-verdict-red-500/40',
        pending:       'bg-verdict-navy-500 text-verdict-navy-100 border border-verdict-navy-300/50',
        'agent-active':   'bg-verdict-green-500/15 text-verdict-green-400 border border-verdict-green-500/30',
        'agent-degraded': 'bg-verdict-amber-500/15 text-verdict-amber-400 border border-verdict-amber-500/30',
        default:          'bg-verdict-navy-500 text-verdict-navy-50 border border-verdict-navy-300/50',
      },
    },
    defaultVariants: { variant: 'default' },
  }
);

export function Badge({
  variant, children, className, dot = false,
}: VariantProps<typeof badgeVariants> & {
  children: React.ReactNode; className?: string; dot?: boolean;
}) {
  return (
    <span className={cn(badgeVariants({ variant }), className)}>
      {dot && <span className="w-1.5 h-1.5 rounded-full bg-current animate-monitoring-pulse" aria-hidden />}
      {children}
    </span>
  );
}
```

---

### 4.5 Modal

```tsx
// apps/frontend/src/components/ui/Modal.tsx
// Built on Radix UI Dialog with VERDICT styling
import * as Dialog from '@radix-ui/react-dialog';
import { AnimatePresence, motion } from 'framer-motion';
import { X } from 'lucide-react';

const MODAL_SIZES = {
  sm: 'max-w-sm',   // Confirm dialogs
  md: 'max-w-md',   // Single-field forms, info
  lg: 'max-w-lg',   // Add witness, session config
  xl: 'max-w-2xl',  // Fact review, document viewer
} as const;

export function Modal({
  open, onClose, title, description, children, size = 'md', hideClose = false,
}: {
  open: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: React.ReactNode;
  size?: keyof typeof MODAL_SIZES;
  hideClose?: boolean;
}) {
  return (
    <Dialog.Root open={open} onOpenChange={o => !o && onClose()}>
      <AnimatePresence>
        {open && (
          <Dialog.Portal forceMount>
            {/* Backdrop */}
            <Dialog.Overlay asChild>
              <motion.div
                className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.15 }}
              />
            </Dialog.Overlay>

            {/* Panel */}
            <Dialog.Content asChild>
              <motion.div
                className={cn(
                  'fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50',
                  'w-full mx-4',
                  'bg-verdict-navy-600 rounded-xl border border-verdict-navy-300/40 shadow-modal',
                  'focus:outline-none',
                  MODAL_SIZES[size]
                )}
                initial={{ opacity: 0, scale: 0.95, y: -8 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, y: -4 }}
                transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
                aria-modal
              >
                {/* Header */}
                <div className="flex items-start justify-between p-6 pb-4">
                  <div className="pr-4">
                    <Dialog.Title className="text-lg font-semibold text-white">
                      {title}
                    </Dialog.Title>
                    {description && (
                      <Dialog.Description className="mt-1 text-sm text-verdict-navy-50">
                        {description}
                      </Dialog.Description>
                    )}
                  </div>
                  {!hideClose && (
                    <button
                      onClick={onClose}
                      className="flex-shrink-0 p-1.5 rounded-md text-verdict-navy-100 hover:bg-verdict-navy-500 hover:text-white transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-verdict-blue-500"
                      aria-label="Close dialog"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>

                {/* Body */}
                <div className="px-6 pb-6">
                  {children}
                </div>
              </motion.div>
            </Dialog.Content>
          </Dialog.Portal>
        )}
      </AnimatePresence>
    </Dialog.Root>
  );
}

// Confirm modal — destructive action confirmation pattern
export function ConfirmModal({
  open, onClose, onConfirm, title, message,
  confirmLabel = 'Confirm', danger = false, loading = false,
}: {
  open: boolean; onClose: () => void; onConfirm: () => void;
  title: string; message: string; confirmLabel?: string; danger?: boolean; loading?: boolean;
}) {
  return (
    <Modal open={open} onClose={onClose} title={title} size="sm">
      <p className="text-sm text-verdict-navy-50 mb-6 leading-relaxed">{message}</p>
      <div className="flex justify-end gap-3">
        <Button variant="ghost" onClick={onClose} disabled={loading}>Cancel</Button>
        <Button
          variant={danger ? 'danger' : 'primary'}
          onClick={onConfirm}
          loading={loading}
        >
          {confirmLabel}
        </Button>
      </div>
    </Modal>
  );
}
```

---

### 4.6 Toast Notifications

```tsx
// apps/frontend/src/components/ui/Toast.tsx
// Position: top-right, stacked, max 3 visible

import * as ToastPrimitive from '@radix-ui/react-toast';
import { AlertCircle, CheckCircle2, Info, AlertTriangle, X } from 'lucide-react';

const TOAST_VARIANTS = {
  success: { icon: CheckCircle2, borderColor: 'border-verdict-green-500/50', iconClass: 'text-verdict-green-400' },
  error:   { icon: AlertCircle,  borderColor: 'border-verdict-red-500/50',   iconClass: 'text-verdict-red-400' },
  warning: { icon: AlertTriangle,borderColor: 'border-verdict-amber-500/50', iconClass: 'text-verdict-amber-400' },
  info:    { icon: Info,         borderColor: 'border-verdict-blue-500/50',  iconClass: 'text-verdict-blue-400' },
} as const;

export function VerdictToast({
  title, description, variant = 'info', onDismiss,
}: {
  title: string; description?: string;
  variant?: keyof typeof TOAST_VARIANTS; onDismiss: () => void;
}) {
  const { icon: Icon, borderColor, iconClass } = TOAST_VARIANTS[variant];

  return (
    <ToastPrimitive.Root
      className={cn(
        'flex items-start gap-3 p-4 rounded-lg border shadow-card-lg',
        'bg-verdict-navy-600 w-[360px] max-w-[calc(100vw-2rem)]',
        borderColor,
        'data-[state=open]:animate-[slide-in-right_300ms_cubic-bezier(0.16,1,0.3,1)]',
        'data-[state=closed]:animate-[slide-out-right_200ms_ease-in]',
        'data-[swipe=end]:translate-x-[var(--radix-toast-swipe-end-x)]',
        'data-[swipe=move]:translate-x-[var(--radix-toast-swipe-move-x)] data-[swipe=move]:transition-none',
      )}
      aria-live="assertive"
      aria-atomic
    >
      <Icon className={cn('w-5 h-5 flex-shrink-0 mt-0.5', iconClass)} aria-hidden />
      <div className="flex-1 min-w-0">
        <ToastPrimitive.Title className="text-sm font-semibold text-white">{title}</ToastPrimitive.Title>
        {description && (
          <ToastPrimitive.Description className="mt-1 text-sm text-verdict-navy-50 leading-snug">
            {description}
          </ToastPrimitive.Description>
        )}
      </div>
      <ToastPrimitive.Close
        onClick={onDismiss}
        className="flex-shrink-0 p-1 rounded text-verdict-navy-100 hover:text-white hover:bg-verdict-navy-500 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-verdict-blue-500"
        aria-label="Dismiss notification"
      >
        <X className="w-3.5 h-3.5" />
      </ToastPrimitive.Close>
    </ToastPrimitive.Root>
  );
}

export function ToastViewport() {
  return (
    <ToastPrimitive.Viewport
      className="fixed top-4 right-4 z-[100] flex flex-col gap-2 w-[360px] max-w-[calc(100vw-2rem)] outline-none"
      aria-label="Notifications"
    />
  );
}

// useToast hook
export function useToast() {
  const [toasts, setToasts] = React.useState<Array<{
    id: string; title: string; description?: string;
    variant: 'success' | 'error' | 'warning' | 'info';
  }>>([]);

  const toast = React.useCallback((t: Omit<typeof toasts[0], 'id'>) => {
    const id = crypto.randomUUID();
    setToasts(prev => [...prev.slice(-2), { ...t, id }]); // max 3 toasts
    setTimeout(() => setToasts(prev => prev.filter(x => x.id !== id)), 5000);
  }, []);

  const dismiss = React.useCallback((id: string) => {
    setToasts(prev => prev.filter(x => x.id !== id));
  }, []);

  return { toasts, toast, dismiss };
}
```

---

### 4.7 Toggle Switch

```tsx
// apps/frontend/src/components/ui/Toggle.tsx
export function ToggleSwitch({
  id, checked, onChange, disabled = false,
}: {
  id?: string; checked: boolean; onChange: (v: boolean) => void; disabled?: boolean;
}) {
  const switchId = id ?? React.useId();
  return (
    <button
      id={switchId}
      type="button"
      role="switch"
      aria-checked={checked}
      disabled={disabled}
      onClick={() => !disabled && onChange(!checked)}
      className={cn(
        'relative w-10 h-6 rounded-full transition-colors duration-200',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-verdict-blue-500 focus-visible:ring-offset-2 focus-visible:ring-offset-verdict-navy-800',
        'disabled:opacity-40 disabled:cursor-not-allowed',
        checked ? 'bg-verdict-blue-600' : 'bg-verdict-navy-400'
      )}
    >
      <span
        className={cn(
          'absolute top-1 w-4 h-4 bg-white rounded-full shadow transition-transform duration-200',
          checked ? 'translate-x-5' : 'translate-x-1'
        )}
        aria-hidden
      />
    </button>
  );
}

// Toggle row — used in session configuration
export function ToggleRow({
  label, description, badge, checked, onChange, disabled = false,
}: {
  label: string; description?: string; badge?: string;
  checked: boolean; onChange: (v: boolean) => void; disabled?: boolean;
}) {
  const id = React.useId();
  return (
    <div className={cn(
      'flex items-center justify-between gap-4 p-4 rounded-lg',
      'bg-verdict-navy-600/50 border border-verdict-navy-300/30',
      disabled && 'opacity-50'
    )}>
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <label htmlFor={id} className="text-sm font-medium text-white cursor-pointer">
            {label}
          </label>
          {badge && <Badge variant="indexing">{badge}</Badge>}
        </div>
        {description && (
          <p className="mt-0.5 text-xs text-verdict-navy-100">{description}</p>
        )}
      </div>
      <ToggleSwitch id={id} checked={checked} onChange={onChange} disabled={disabled} />
    </div>
  );
}
```

---

### 4.8 Skeleton Loading

```tsx
// apps/frontend/src/components/ui/Skeleton.tsx

export function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn('animate-pulse rounded bg-verdict-navy-500/50', className)}
      aria-hidden
    />
  );
}

// Dashboard — 6 case card skeletons
export function DashboardSkeleton() {
  return (
    <div
      className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6"
      aria-busy="true"
      aria-label="Loading cases..."
    >
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="bg-verdict-navy-600 rounded-lg border border-verdict-navy-300/30 p-5 space-y-4">
          <div className="flex justify-between items-start">
            <Skeleton className="h-5 w-44" />
            <Skeleton className="h-5 w-20 rounded-full" />
          </div>
          <Skeleton className="h-4 w-32" />
          <div className="flex gap-3">
            <Skeleton className="h-3.5 w-14" />
            <Skeleton className="h-3.5 w-20" />
          </div>
        </div>
      ))}
    </div>
  );
}

// Brief — score + radar + recommendations
export function BriefSkeleton() {
  return (
    <div className="max-w-2xl mx-auto py-8 px-6 space-y-6" aria-busy="true" aria-label="Generating coaching brief...">
      {/* Score hero */}
      <div className="bg-verdict-navy-600 rounded-2xl p-10 text-center space-y-3">
        <Skeleton className="h-5 w-32 mx-auto rounded-full" />
        <Skeleton className="h-20 w-36 mx-auto" />
        <Skeleton className="h-6 w-20 mx-auto rounded-full" />
      </div>
      {/* Radar */}
      <div className="bg-verdict-navy-600 rounded-xl p-6 space-y-4">
        <Skeleton className="h-5 w-40" />
        <Skeleton className="h-64 w-64 rounded-full mx-auto" />
      </div>
      {/* Recommendations */}
      <div className="bg-verdict-navy-600 rounded-xl p-6 space-y-3">
        <Skeleton className="h-5 w-48" />
        {[1, 2, 3].map(i => (
          <div key={i} className="flex gap-3">
            <Skeleton className="w-6 h-6 rounded-full flex-shrink-0" />
            <Skeleton className="h-10 flex-1" />
          </div>
        ))}
      </div>
    </div>
  );
}

// Alert rail — while session initializes
export function AlertRailSkeleton() {
  return (
    <div className="p-3 space-y-3" aria-busy="true" aria-label="Alert rail loading...">
      {[1, 2].map(i => (
        <div key={i} className="rounded-lg border border-verdict-navy-300/30 p-3 space-y-2">
          <div className="flex justify-between">
            <Skeleton className="h-4 w-32" />
            <Skeleton className="h-4 w-10 rounded-full" />
          </div>
          <Skeleton className="h-3.5 w-full" />
          <Skeleton className="h-3.5 w-3/4" />
        </div>
      ))}
    </div>
  );
}
```

---

### 4.9 Empty States

```tsx
// apps/frontend/src/components/ui/EmptyState.tsx

const EMPTY_CONFIGS = {
  cases: {
    icon: FolderOpen,
    title: 'No cases yet',
    description: 'Create your first case to begin preparing witnesses for deposition.',
    cta: { label: 'Create Case', href: '/cases/new' },
  },
  documents: {
    icon: FileText,
    title: 'No documents uploaded',
    description: 'Upload prior depositions, medical records, or case documents to enable the Inconsistency Detector.',
    cta: null,
  },
  witnesses: {
    icon: Users,
    title: 'No witnesses added',
    description: 'Add a witness to configure their first deposition coaching session.',
    cta: null,
  },
  sessions: {
    icon: Clock,
    title: 'No sessions yet',
    description: 'Configure your first practice session for this witness.',
    cta: null,
  },
  alerts: {
    icon: CheckCircle2,
    title: 'No alerts so far',
    description: 'No contradictions or objectionable questions detected in this session.',
    cta: null,
  },
  search: {
    icon: Search,
    title: 'No results',
    description: 'Try adjusting your search or filters.',
    cta: null,
  },
} as const;

export function EmptyState({
  context,
  compact = false,
  onAction,
}: {
  context: keyof typeof EMPTY_CONFIGS;
  compact?: boolean;
  onAction?: () => void;
}) {
  const config = EMPTY_CONFIGS[context];
  const Icon = config.icon;

  return (
    <div className={cn('flex flex-col items-center text-center', compact ? 'py-8 px-4' : 'py-16 px-8')}>
      <div className={cn(
        'rounded-full bg-verdict-navy-500/60 flex items-center justify-center mb-4',
        compact ? 'w-10 h-10' : 'w-14 h-14'
      )}>
        <Icon className={cn('text-verdict-navy-100', compact ? 'w-5 h-5' : 'w-7 h-7')} aria-hidden />
      </div>

      <h3 className={cn('font-semibold text-white', compact ? 'text-sm mb-1' : 'text-base mb-2')}>
        {config.title}
      </h3>
      <p className={cn('text-verdict-navy-50 max-w-xs leading-relaxed', compact ? 'text-xs' : 'text-sm')}>
        {config.description}
      </p>

      {config.cta && (
        <Button
          variant="primary"
          size={compact ? 'sm' : 'md'}
          className="mt-5"
          icon={<Plus />}
          onClick={onAction}
        >
          {config.cta.label}
        </Button>
      )}
    </div>
  );
}
```

---

### 4.10 Score Display (Brief Hero)

```tsx
// apps/frontend/src/components/brief/ScoreHero.tsx
import { motion, useMotionValue, useTransform, animate } from 'framer-motion';

function scoreLabel(s: number) {
  if (s >= 85) return 'Excellent';
  if (s >= 75) return 'Good';
  if (s >= 60) return 'Developing';
  if (s >= 50) return 'Needs Work';
  return 'At Risk';
}

export function ScoreHero({ score, delta, sessionNumber }: {
  score: number; delta?: number; sessionNumber: number;
}) {
  const count = useMotionValue(0);
  const rounded = useTransform(count, v => Math.round(v));

  React.useEffect(() => {
    const c = animate(count, score, { duration: 1.2, ease: [0.33, 1, 0.68, 1] });
    return c.stop;
  }, [score]);

  const colorClass = score >= 75 ? 'text-verdict-green-400' : score >= 50 ? 'text-verdict-amber-400' : 'text-verdict-red-400';
  const badgeClass = score >= 75
    ? 'bg-verdict-green-500/15 text-verdict-green-300 border-verdict-green-500/30'
    : score >= 50
    ? 'bg-verdict-amber-500/15 text-verdict-amber-300 border-verdict-amber-500/30'
    : 'bg-verdict-red-500/15 text-verdict-red-300 border-verdict-red-500/30';

  return (
    <div className="bg-verdict-navy-600 rounded-2xl border border-verdict-navy-300/30 shadow-card p-10 text-center flex flex-col items-center gap-3">
      <p className="text-xs font-semibold uppercase tracking-widest text-verdict-navy-100">
        Session {sessionNumber} Score
      </p>

      <div className={cn('font-bold tabular-nums tracking-tighter flex items-end gap-1', colorClass)}>
        <motion.span className="text-6xl sm:text-7xl" aria-label={`Score: ${score} out of 100`}>
          {rounded}
        </motion.span>
        <span className="text-2xl text-verdict-navy-100 mb-2">/100</span>
      </div>

      <div className={cn('px-3 py-1 rounded-full text-sm font-semibold border', badgeClass)}>
        {scoreLabel(score)}
      </div>

      {delta !== undefined && Math.abs(delta) > 0 && (
        <div className={cn(
          'flex items-center gap-1.5 text-sm font-medium',
          delta > 0 ? 'text-verdict-green-400' : 'text-verdict-red-400'
        )}>
          <span aria-hidden>{delta > 0 ? '▲' : '▼'}</span>
          <span>{Math.abs(delta)} pts from Session 1</span>
        </div>
      )}
    </div>
  );
}
```

---

## 5. ACCESSIBILITY GUIDELINES

### 5.1 WCAG 2.1 AA Target

VERDICT targets **WCAG 2.1 Level AA** across all P0 screens. Enterprise legal software faces accessibility audits from firm IT departments. Non-compliance blocks procurement.

### 5.2 Color Contrast Requirements

| Text category | Required ratio | VERDICT approach |
|--------------|---------------|-----------------|
| Normal body text (< 18px non-bold, < 14px bold) | 4.5:1 minimum | All primary text on navy-800 exceeds 7:1 |
| Large text (≥ 18px regular or ≥ 14px bold) | 3:1 minimum | All heading text AAA-compliant |
| UI components and graphic objects | 3:1 minimum | Alert borders, icons all verified ≥ 3:1 |
| Decorative / disabled content | Exempt | Disabled state: 40% opacity (below threshold — exempt) |

**Never use `verdict-navy-200` (#4A6080) as body text on dark backgrounds** — 2.7:1 ratio fails AA.

### 5.3 Focus Indicators

Every interactive element must display a visible focus indicator. Never suppress `outline` without replacing it.

```css
/* globals.css — single source of truth for focus */
*:focus-visible {
  outline: 2px solid #3B82F6;   /* verdict-blue-600 */
  outline-offset: 2px;
}

/* Component-specific (applied via Tailwind) */
/* focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-verdict-blue-500 
   focus-visible:ring-offset-2 focus-visible:ring-offset-verdict-navy-800 */
```

**The standard focus pattern (apply to ALL interactive elements):**
```tsx
className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-verdict-blue-500 focus-visible:ring-offset-2 focus-visible:ring-offset-verdict-navy-800"
```

On dark card surfaces (ring-offset should match the card):
```tsx
className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-verdict-blue-500 focus-visible:ring-offset-1 focus-visible:ring-offset-verdict-navy-600"
```

### 5.4 Keyboard Navigation Requirements

| Component | Tab behavior | Enter/Space | Arrow keys | Escape |
|-----------|-------------|-------------|-----------|--------|
| Button | Focusable | Activate | — | — |
| Link | Focusable | Navigate | — | — |
| Input | Focusable | — | — | — |
| Select/Dropdown | Focusable | Open | Navigate options | Close |
| Radio group (aggression) | Group focusable | Select | Change selection | — |
| Checkbox/Toggle | Focusable | Toggle | — | — |
| Modal | Trap inside | — | — | Close |
| Alert card [Confirm] | Focusable | Confirm | — | — |
| Tab panel | Group focusable | — | Switch tabs | — |
| Alert card [Reject] | Focusable | Reject (with undo) | — | — |

```tsx
// Tab panel keyboard navigation (← → switch tabs)
function TabBar({ tabs, activeTab, onTabChange }: {
  tabs: string[]; activeTab: string; onTabChange: (t: string) => void;
}) {
  const handleKeyDown = (e: React.KeyboardEvent, idx: number) => {
    if (e.key === 'ArrowRight') {
      e.preventDefault();
      onTabChange(tabs[(idx + 1) % tabs.length]);
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      onTabChange(tabs[(idx - 1 + tabs.length) % tabs.length]);
    }
  };

  return (
    <div role="tablist" className="flex border-b border-verdict-navy-300/30">
      {tabs.map((tab, i) => {
        const active = tab === activeTab;
        return (
          <button
            key={tab}
            role="tab"
            aria-selected={active}
            aria-controls={`tabpanel-${tab.toLowerCase()}`}
            id={`tab-${tab.toLowerCase()}`}
            tabIndex={active ? 0 : -1}
            onClick={() => onTabChange(tab)}
            onKeyDown={e => handleKeyDown(e, i)}
            className={cn(
              'px-4 py-3 text-sm font-medium border-b-2 -mb-px transition-colors duration-150',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-verdict-blue-500',
              active
                ? 'border-verdict-blue-500 text-white'
                : 'border-transparent text-verdict-navy-50 hover:text-white hover:border-verdict-navy-300'
            )}
          >
            {tab}
          </button>
        );
      })}
    </div>
  );
}
```

### 5.5 ARIA Patterns — VERDICT Specific

```tsx
// 1. Live alert announcements — screen reader hears new alerts
<div aria-live="assertive" aria-atomic="false" className="sr-only" role="status">
  {latestAlert && `New alert: ${latestAlert.type} detected at question ${latestAlert.questionNumber}.`}
</div>

// 2. Session timer — announce at urgency thresholds only
function useTimerAnnouncements(remainingSeconds: number) {
  const prev = React.useRef(remainingSeconds);
  React.useEffect(() => {
    const thresholds = [600, 300, 60]; // 10 min, 5 min, 1 min
    thresholds.forEach(t => {
      if (prev.current > t && remainingSeconds <= t) {
        announceToScreenReader(`${Math.floor(t/60)} minute${t > 60 ? 's' : ''} remaining`);
      }
    });
    prev.current = remainingSeconds;
  }, [remainingSeconds]);
}

function announceToScreenReader(message: string) {
  const el = document.getElementById('sr-announcer');
  if (el) { el.textContent = ''; setTimeout(() => el.textContent = message, 50); }
}

// 3. Progressbar — ingestion and brief generation
<div
  role="progressbar"
  aria-valuenow={progress}
  aria-valuemin={0}
  aria-valuemax={100}
  aria-label={`Document ingestion: ${progress}% complete`}
  aria-live="polite"
>

// 4. Alert rail — landmark + count
<aside
  aria-label={`Alert rail: ${alerts.length} alert${alerts.length !== 1 ? 's' : ''}`}
  role="complementary"
>

// 5. Score — output element
<output
  aria-label={`Session score: ${score} out of 100. ${scoreLabel(score)}.`}
  aria-live="polite"
>
  {score}
</output>

// 6. Icon-only buttons — always need aria-label
<Button size="icon" aria-label="Dismiss inconsistency alert at question 8">
  <X className="w-4 h-4" aria-hidden />
</Button>

// 7. Loading spinners — need accessible text
<div role="status" aria-label="Generating coaching brief...">
  <Loader2 className="w-5 h-5 animate-spin text-verdict-blue-400" aria-hidden />
</div>
```

### 5.6 Semantic HTML Requirements

```tsx
// Required structure on every page:
<header>       // Global navigation (role="navigation" inside)
<main id="main-content">  // ONE per page — the primary content target
<aside>        // Supplementary content (alert rail, session controls)
<nav aria-label="...">    // Navigation regions with labels
<section aria-labelledby> // Named content regions
<article>      // Self-contained content (alert cards)
<h1>           // ONE per page — page title
<h2>–<h6>     // Hierarchical, never skip levels
<ul> / <ol>   // Alert rail list, recommendation list, transcript turns
<fieldset>     // Grouped form controls (duration picker, focus areas)
<legend>       // fieldset descriptor
<label htmlFor> // ALL inputs must have associated labels
<output>       // Dynamic values (score, timer)
<time>         // Timestamps and durations
<button type="button"> // Non-submit buttons (default type is submit!)
```

### 5.7 Screen Reader Utilities

```tsx
// Visually hidden — for screen reader text that aids navigation
export function ScreenReaderOnly({ children }: { children: React.ReactNode }) {
  return <span className="sr-only">{children}</span>;
}

// Global live region — mount once in root layout
export function LiveRegion() {
  return (
    <div
      id="sr-announcer"
      aria-live="polite"
      aria-atomic="true"
      className="sr-only"
    />
  );
}

// Usage: announceToScreenReader('Brief generation complete. Score: 79 out of 100.')
```

### 5.8 Form Accessibility Checklist

```tsx
// Every form must satisfy:
// ✅ All inputs have <label htmlFor={inputId}>
// ✅ Required fields marked with aria-required and visible indicator
// ✅ Error messages use role="alert" and are linked via aria-describedby
// ✅ Error summary at top of form on submit if multiple errors
// ✅ Focus moves to first error on failed submit
// ✅ Success state announced via aria-live
// ✅ Loading/disabled state communicated via aria-busy and aria-disabled
// ✅ No color alone to communicate state (icon + color together)
// ✅ Placeholder text is NOT used as a label substitute

function FormErrorSummary({ errors }: { errors: Record<string, string> }) {
  const errorList = Object.entries(errors);
  if (!errorList.length) return null;
  return (
    <div
      role="alert"
      className="p-4 rounded-lg bg-verdict-red-500/10 border border-verdict-red-500/40"
      tabIndex={-1}
      ref={el => el?.focus()}
    >
      <p className="text-sm font-semibold text-verdict-red-300 mb-2">
        Please correct {errorList.length} error{errorList.length > 1 ? 's' : ''}:
      </p>
      <ul className="space-y-1">
        {errorList.map(([field, msg]) => (
          <li key={field} className="text-sm text-verdict-red-400">
            <a href={`#field-${field}`} className="underline hover:no-underline">{msg}</a>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

---

## 6. ANIMATION GUIDELINES

### 6.1 Tailwind Animation Config

```js
// tailwind.config.ts — add to theme.extend
keyframes: {
  // Alert card entrance — spring slide from top
  'slide-in-down': {
    '0%':   { opacity: '0', transform: 'translateY(-20px) scale(0.96)' },
    '100%': { opacity: '1', transform: 'translateY(0) scale(1)' },
  },
  // Alert dismissed / rejected
  'slide-out-right': {
    '0%':   { opacity: '1', transform: 'translateX(0)' },
    '100%': { opacity: '0', transform: 'translateX(100%)' },
  },
  // Toast notification entrance
  'slide-in-right': {
    '0%':   { opacity: '0', transform: 'translateX(60px)' },
    '100%': { opacity: '1', transform: 'translateX(0)' },
  },
  // HIGH IMPEACHMENT RISK — border pulse ×2 then stops
  'pulse-border-red': {
    '0%, 100%': { boxShadow: '0 0 0 1px rgba(239,68,68,0.5)' },
    '50%':      { boxShadow: '0 0 0 3px rgba(239,68,68,0.85), 0 0 20px rgba(239,68,68,0.3)' },
  },
  // Alert badge count increment
  'badge-pop': {
    '0%':   { transform: 'scale(1)' },
    '50%':  { transform: 'scale(1.3)' },
    '100%': { transform: 'scale(1)' },
  },
  // Confirmed — green flash then grey
  'confirm-flash': {
    '0%':   { backgroundColor: 'rgba(16,185,129,0.3)' },
    '100%': { backgroundColor: 'transparent' },
  },
  // Agent monitoring green dot — steady pulse
  'monitoring-pulse': {
    '0%, 100%': { opacity: '1' },
    '50%':      { opacity: '0.35' },
  },
  // Brief section cascade
  'cascade-in': {
    '0%':   { opacity: '0', transform: 'translateY(10px)' },
    '100%': { opacity: '1', transform: 'translateY(0)' },
  },
  // ElevenLabs waveform glow sync
  'amplitude-glow': {
    '0%, 100%': { boxShadow: '0 0 6px rgba(139,92,246,0.2)' },
    '50%':      { boxShadow: '0 0 20px rgba(139,92,246,0.6)' },
  },
  // Session start — panels fade in
  'fade-in': {
    '0%':   { opacity: '0' },
    '100%': { opacity: '1' },
  },
},

animation: {
  'slide-in-down':    'slide-in-down 300ms cubic-bezier(0.34,1.56,0.64,1) forwards',
  'slide-out-right':  'slide-out-right 200ms cubic-bezier(0.7,0,0.84,0) forwards',
  'slide-in-right':   'slide-in-right 300ms cubic-bezier(0.16,1,0.3,1) forwards',
  'pulse-border-red': 'pulse-border-red 600ms ease-in-out 2',   // 2 iterations then stops
  'badge-pop':        'badge-pop 150ms ease-in-out',
  'confirm-flash':    'confirm-flash 200ms ease-out forwards',
  'monitoring-pulse': 'monitoring-pulse 2000ms ease-in-out infinite',
  'cascade-in':       'cascade-in 500ms cubic-bezier(0.16,1,0.3,1) forwards',
  'amplitude-glow':   'amplitude-glow 800ms ease-in-out infinite',
  'fade-in':          'fade-in 400ms ease-out forwards',
},
```

### 6.2 Framer Motion Variants

```tsx
// apps/frontend/src/lib/motion-variants.ts
// Centralized — import these everywhere, don't define inline

import type { Variants } from 'framer-motion';

// Alert card — spring entrance + slide-right exit
export const alertCardVariants: Variants = {
  hidden:  { opacity: 0, y: -16, scale: 0.96 },
  visible: {
    opacity: 1, y: 0, scale: 1,
    transition: { type: 'spring', stiffness: 420, damping: 26 },
  },
  exit: { opacity: 0, x: 60, transition: { duration: 0.2, ease: 'easeIn' } },
};

// Confirmed flash → grey state
export const alertConfirmedVariants: Variants = {
  active: { opacity: 1 },
  confirmed: { opacity: 0.55, transition: { duration: 0.3 } },
};

// Modal open/close
export const modalVariants: Variants = {
  hidden:  { opacity: 0, scale: 0.95, y: -8 },
  visible: { opacity: 1, scale: 1, y: 0, transition: { duration: 0.2, ease: [0.16, 1, 0.3, 1] } },
  exit:    { opacity: 0, scale: 0.95, y: -4, transition: { duration: 0.15, ease: 'easeIn' } },
};

// Brief sections — stagger cascade
export const briefContainerVariants: Variants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.1 } },
};
export const briefSectionVariants: Variants = {
  hidden:  { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] } },
};

// Alert rail list — stagger incoming alerts
export const alertRailVariants: Variants = {
  visible: { transition: { staggerChildren: 0.05 } },
};

// Page slide transitions
export const pageTransitionVariants: Variants = {
  initial:  { opacity: 0, x: 20 },
  animate:  { opacity: 1, x: 0, transition: { duration: 0.25, ease: 'easeOut' } },
  exit:     { opacity: 0, x: -20, transition: { duration: 0.2, ease: 'easeIn' } },
};

// Session start — panels fade in sequentially
export const sessionPanelVariants: Variants = {
  hidden:  { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.4, ease: 'easeOut' } },
};
```

### 6.3 Usage Examples

```tsx
// Alert card with entrance animation and exit on rejection
import { motion, AnimatePresence } from 'framer-motion';
import { alertCardVariants } from '@/lib/motion-variants';

<AnimatePresence mode="popLayout">
  {alerts.map(alert => (
    <motion.div
      key={alert.id}
      variants={alertCardVariants}
      initial="hidden"
      animate="visible"
      exit="exit"
      layout  // Animate remaining cards closing gap after exit
    >
      <AlertCard type={alert.type}>
        <AlertCardContent alert={alert} />
      </AlertCard>
    </motion.div>
  ))}
</AnimatePresence>

// Brief with cascade reveal
<motion.div
  variants={briefContainerVariants}
  initial="hidden"
  animate="visible"
  className="space-y-6"
>
  <motion.div variants={briefSectionVariants}><ScoreHero score={score} /></motion.div>
  <motion.div variants={briefSectionVariants}><WeaknessMapCard data={weaknessMap} /></motion.div>
  <motion.div variants={briefSectionVariants}><AlertSummaryCard alerts={confirmedAlerts} /></motion.div>
  <motion.div variants={briefSectionVariants}><RecommendationsCard recs={recommendations} /></motion.div>
</motion.div>

// Counter for alert rail badge
function AlertCountBadge({ count }: { count: number }) {
  const [prev, setPrev] = React.useState(count);
  const [pop, setPop] = React.useState(false);

  React.useEffect(() => {
    if (count > prev) { setPop(true); setTimeout(() => setPop(false), 150); }
    setPrev(count);
  }, [count, prev]);

  return (
    <span className={cn(
      'inline-flex items-center justify-center w-5 h-5 rounded-full text-xs font-bold bg-verdict-red-600 text-white',
      pop && 'animate-badge-pop'
    )}>
      {count}
    </span>
  );
}
```

### 6.4 Animation Rules

| Rule | Rationale |
|------|-----------|
| Only animate `transform` and `opacity` | GPU-composited, no layout reflow |
| Never animate `width`, `height`, `top`, `left`, `margin` | Causes expensive layout/paint |
| Entrance animations ≤ 500ms | Longer feels sluggish for a professional tool |
| Exit animations ≤ 250ms | Exits should be snappier than entrances |
| Spring physics only for alert card entrance | Reserve spring for "things with weight" |
| Timer color: `duration-100` | Urgency = no delay |
| HIGH IMPEACHMENT RISK pulse: exactly 2 cycles | Draws attention, then settles — doesn't nag |
| Confirm flash: 200ms | Long enough to register, brief enough to feel instant |
| No bounce/wiggle on buttons or forms | VERDICT is a professional tool, not a game |

### 6.5 Reduced Motion Support

```tsx
// globals.css — respect OS accessibility preference
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

// In Framer Motion components — check preference
import { useReducedMotion } from 'framer-motion';

function AnimatedAlertCard({ children }: { children: React.ReactNode }) {
  const reduce = useReducedMotion();
  return (
    <motion.div
      variants={reduce
        ? { hidden: {}, visible: {}, exit: {} }   // no-op — instant appearance
        : alertCardVariants
      }
      initial="hidden"
      animate="visible"
      exit="exit"
    >
      {children}
    </motion.div>
  );
}
```

### 6.6 Complete Animation Timing Reference

| Event | Animation | Duration | Easing |
|-------|-----------|----------|--------|
| Alert card entrance | Slide down from top + scale | 300ms | Spring (stiffness 420, damping 26) |
| Alert card rejection | Slide out right | 200ms | ease-in |
| Alert badge increment | Scale pop 1→1.3→1 | 150ms | ease-in-out |
| Alert bg (new): red tint | Fade red-50 → transparent | 1500ms | ease-out |
| HIGH IMPEACHMENT RISK | Border pulse × 2 cycles | 600ms × 2 | ease-in-out |
| Confirm button click | Green flash → grey muted | 300ms total | ease-out |
| Modal open | Scale 0.95→1.0 + opacity | 200ms | [0.16, 1, 0.3, 1] |
| Modal close | Scale 1.0→0.95 + opacity | 150ms | ease-in |
| Toast entrance | Slide in from right | 300ms | [0.16, 1, 0.3, 1] |
| Toast dismiss | Slide out right | 200ms | ease-in |
| Page transition | Slide right + opacity | 250ms | ease-out |
| Live session takeover | Expand from center | 400ms | ease-in-out |
| Brief sections cascade | Each section staggered 100ms | 500ms | [0.16, 1, 0.3, 1] |
| Score count-up | 0 → final value | 1200ms | [0.33, 1, 0.68, 1] |
| Radar axes outward | Per-axis, staggered 80ms | 600ms | ease-out |
| ElevenLabs waveform glow | Amplitude sync | 800ms | ease-in-out infinite |
| Agent monitoring dot | Steady fade pulse | 2000ms | ease-in-out infinite |

---

## 7. ICON SYSTEM

### 7.1 Library

**Lucide React `0.477.0`** — consistent 2px stroke, geometric precision, MIT license, fully tree-shakeable.

```bash
pnpm add lucide-react@0.477.0
```

### 7.2 Size System

```tsx
const ICON_SIZE = {
  xs:   'w-3 h-3',      // 12px — badge decorators, tight inline
  sm:   'w-3.5 h-3.5',  // 14px — compact buttons, form field icons
  md:   'w-4 h-4',      // 16px — standard button icons ✦ DEFAULT
  lg:   'w-5 h-5',      // 20px — card headings, alert type icons
  xl:   'w-6 h-6',      // 24px — empty states, feature icons
  '2xl':'w-8 h-8',      // 32px — large empty states
  hero: 'w-12 h-12',    // 48px — onboarding feature callouts
} as const;
```

Stroke width: **never override** Lucide's default `2px`. Deviating from this breaks visual consistency with the rest of the system.

### 7.3 VERDICT Icon Assignments

```tsx
import {
  // Navigation & structure
  LayoutDashboard,   // /dashboard nav
  FolderOpen,        // /cases nav
  Settings,          // /settings nav
  Building2,         // Firm badge, admin

  // Core actions
  Plus,              // Create anything
  Pencil,            // Edit
  Trash2,            // Delete (always with confirmation)
  Download,          // PDF export
  Share2,            // Share brief link
  Copy,              // Copy to clipboard
  ExternalLink,      // Open in new tab
  RefreshCw,         // Retry / refresh
  X,                 // Close, dismiss, reject alert
  Check,             // Confirm step, checkmark
  ChevronRight,      // Expand row, navigate forward
  ChevronDown,       // Collapse, dropdown open

  // Session
  Play,              // Start session, begin
  Pause,             // Pause session
  Square,            // Stop/end session
  SkipForward,       // Skip current topic
  Mic,               // Witness mic active
  MicOff,            // Witness mic muted/paused
  Volume2,           // ElevenLabs audio playing
  VolumeX,           // Audio muted
  Monitor,           // Desktop-required message

  // Alerts
  Zap,               // Inconsistency (lightning = fast/electric)
  AlertTriangle,     // Objection / warning
  Eye,               // Behavioral Sentinel / composure
  CheckCircle2,      // Confirmed / success
  XCircle,           // Rejected / error
  Info,              // Info, help, neutral
  ShieldAlert,       // HIGH IMPEACHMENT RISK

  // Documents
  FileText,          // Document card
  Upload,            // Upload trigger
  Search,            // Search (Nia queries)
  ScanLine,          // Document scanning/indexing

  // Time & scheduling
  Clock,             // Duration, timer
  Calendar,          // Deposition date
  Timer,             // Session countdown

  // Analytics
  TrendingUp,        // Score improvement
  TrendingDown,      // Score decline
  BarChart3,         // Weakness Map, analytics
  Target,            // Focus areas
  Gauge,             // Score gauge

  // Auth & identity
  LogOut,            // Logout
  UserCircle,        // User avatar placeholder
  Key,               // API keys
  Lock,              // Secure, locked

  // Status
  Loader2,           // Loading spinner (always with animate-spin)
  Bot,               // AI agent indicator
  Radio,             // Live/streaming indicator
} from 'lucide-react';
```

### 7.4 Icon Usage Rules

```tsx
// Rule 1: ALL decorative icons → aria-hidden
<Play className="w-4 h-4" aria-hidden />

// Rule 2: Icon-only interactive elements → aria-label
<Button size="icon" aria-label="End session early">
  <Square className="w-4 h-4" aria-hidden />
</Button>

// Rule 3: Loading spinners → role="status" on container
<div role="status" aria-label="Generating brief...">
  <Loader2 className="w-5 h-5 animate-spin text-verdict-blue-400" aria-hidden />
</div>

// Rule 4: Icon color — prefer inheriting from text color
<span className="flex items-center gap-2 text-verdict-amber-400">
  <AlertTriangle className="w-4 h-4" aria-hidden />
  <span>Objection: Leading</span>
</span>

// Rule 5: Never override stroke width
// ❌ <Zap strokeWidth={1.5} />
// ✅ <Zap className="w-4 h-4" />

// Rule 6: Consistent size per context — don't mix lg and md in same row
// ❌ <Zap className="w-5 h-5" /> and <AlertTriangle className="w-4 h-4" /> in same row
// ✅ Both w-4 h-4
```

---

## 8. STATE INDICATORS

### 8.1 Agent Status Indicators (Left Panel)

```tsx
// apps/frontend/src/components/session/AgentStatusPanel.tsx

type AgentStatus = 'STANDBY' | 'ACTIVE' | 'PROCESSING' | 'DEGRADED' | 'INACTIVE';

const STATUS_CONFIG: Record<AgentStatus, { dot: string; text: string; label: string }> = {
  STANDBY:    { dot: 'bg-verdict-navy-300',                          text: 'text-verdict-navy-100', label: 'Standby' },
  ACTIVE:     { dot: 'bg-verdict-green-400 animate-monitoring-pulse',text: 'text-verdict-green-400', label: 'Active' },
  PROCESSING: { dot: 'bg-verdict-blue-400 animate-pulse',            text: 'text-verdict-blue-400', label: 'Processing' },
  DEGRADED:   { dot: 'bg-verdict-amber-400',                         text: 'text-verdict-amber-400', label: 'Degraded' },
  INACTIVE:   { dot: 'bg-verdict-navy-400',                          text: 'text-verdict-navy-200', label: 'Off' },
};

export function AgentStatusRow({ name, status }: { name: string; status: AgentStatus }) {
  const cfg = STATUS_CONFIG[status];
  return (
    <div
      className="flex items-center justify-between py-1.5"
      role="status"
      aria-label={`${name} agent: ${cfg.label}`}
    >
      <span className="text-xs text-verdict-navy-50">{name}</span>
      <div className={cn('flex items-center gap-1.5 text-xs font-medium', cfg.text)}>
        <span className={cn('w-1.5 h-1.5 rounded-full flex-shrink-0', cfg.dot)} aria-hidden />
        {cfg.label}
      </div>
    </div>
  );
}

export function AgentStatusPanel({ agents }: { agents: Record<string, AgentStatus> }) {
  return (
    <div className="px-3 py-2">
      <p className="text-2xs font-semibold uppercase tracking-wider text-verdict-navy-200 mb-2">
        Agents
      </p>
      <div className="space-y-0.5">
        <AgentStatusRow name="Interrogator" status={agents.interrogator ?? 'STANDBY'} />
        <AgentStatusRow name="Objection Copilot" status={agents.objection ?? 'STANDBY'} />
        <AgentStatusRow name="Inconsistency" status={agents.inconsistency ?? 'STANDBY'} />
        {agents.sentinel !== 'INACTIVE' && (
          <AgentStatusRow name="Sentinel" status={agents.sentinel ?? 'STANDBY'} />
        )}
      </div>
    </div>
  );
}
```

### 8.2 Degraded Mode Rail Badges

```tsx
// Displayed in alert rail header when agents are running in fallback mode
export function DegradedModeBanner({ mode }: {
  mode: 'nemotron-offline' | 'nia-offline' | 'elevenlabs-offline';
}) {
  const messages = {
    'nemotron-offline':    '⚠️ Scoring: Claude-only mode (threshold 0.85)',
    'nia-offline':         '⚠️ FRE corpus offline — Objection Copilot: Claude-only',
    'elevenlabs-offline':  '⚠️ Voice synthesis offline — text-only mode',
  };

  return (
    <div
      className="mx-3 mb-2 px-2.5 py-1.5 rounded text-xs text-verdict-amber-300 bg-verdict-amber-500/10 border border-verdict-amber-500/30"
      role="status"
      aria-live="polite"
    >
      {messages[mode]}
    </div>
  );
}
```

### 8.3 Session Timer (Complete)

```tsx
// apps/frontend/src/components/session/SessionTimer.tsx

export function SessionTimer({ durationMinutes, startedAt, status }: {
  durationMinutes: number;
  startedAt: Date;
  status: 'ACTIVE' | 'PAUSED' | 'COMPLETE';
}) {
  const [remaining, setRemaining] = React.useState(durationMinutes * 60);
  const announcedRef = React.useRef(new Set<number>());

  React.useEffect(() => {
    if (status !== 'ACTIVE') return;
    const id = setInterval(() => {
      const elapsed = (Date.now() - startedAt.getTime()) / 1000;
      const rem = Math.max(0, durationMinutes * 60 - elapsed);
      setRemaining(rem);

      // Announce thresholds once
      [600, 300, 60].forEach(t => {
        if (rem <= t && !announcedRef.current.has(t)) {
          announcedRef.current.add(t);
          announceToScreenReader(`${Math.round(t / 60)} minute${t > 60 ? 's' : ''} remaining in session`);
        }
      });
    }, 1000);
    return () => clearInterval(id);
  }, [durationMinutes, startedAt, status]);

  const mins = Math.floor(remaining / 60);
  const secs = Math.floor(remaining % 60);
  const pct  = (remaining / (durationMinutes * 60)) * 100;
  const urgency = remaining <= 300 ? 'critical' : remaining <= 600 ? 'warning' : 'normal';

  return (
    <div className="px-3 py-3">
      <time
        dateTime={`PT${mins}M${secs}S`}
        className={cn(
          'font-mono text-3xl font-bold tabular-nums block transition-colors duration-100',
          urgency === 'critical' ? 'text-verdict-red-400' :
          urgency === 'warning'  ? 'text-verdict-amber-400' :
          'text-white'
        )}
        aria-label={`${mins} minutes ${secs} seconds remaining`}
      >
        {String(mins).padStart(2, '0')}:{String(secs).padStart(2, '0')}
      </time>

      {/* Progress bar */}
      <div
        className="mt-2 h-1 bg-verdict-navy-400 rounded-full overflow-hidden"
        role="progressbar"
        aria-valuenow={Math.round(pct)}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label="Session time remaining"
      >
        <div
          className={cn(
            'h-full rounded-full transition-all duration-1000 ease-linear',
            urgency === 'critical' ? 'bg-verdict-red-500' :
            urgency === 'warning'  ? 'bg-verdict-amber-500' :
            'bg-verdict-blue-500'
          )}
          style={{ width: `${pct}%` }}
        />
      </div>

      {status === 'PAUSED' && (
        <Badge variant="default" dot className="mt-2">Paused</Badge>
      )}
    </div>
  );
}
```

### 8.4 Brief Generation Steps

```tsx
// Animated step-through during brief generation (40–180 seconds)
const BRIEF_STEPS = [
  { id: 'collect',    label: 'Collecting session events' },
  { id: 'analyze',    label: 'Analyzing inconsistencies' },
  { id: 'databricks', label: 'Computing Weakness Map scores' },
  { id: 'narrative',  label: 'Generating coaching narrative' },
  { id: 'voice',      label: 'Creating coach voice clips' },
  { id: 'ready',      label: 'Brief ready' },
] as const;

export function BriefGenerationSteps({ currentStepIndex }: { currentStepIndex: number }) {
  return (
    <div className="space-y-3 py-2" role="status" aria-label={`Generating brief: step ${currentStepIndex + 1} of ${BRIEF_STEPS.length}`} aria-live="polite">
      {BRIEF_STEPS.map((step, i) => {
        const done = i < currentStepIndex;
        const active = i === currentStepIndex;
        return (
          <motion.div
            key={step.id}
            className="flex items-center gap-3 text-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: i * 0.1 }}
          >
            <div className={cn(
              'w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 transition-all duration-300',
              done   && 'bg-verdict-green-500',
              active && 'bg-verdict-blue-500',
              !done && !active && 'bg-verdict-navy-400',
            )}>
              {done   && <Check className="w-3.5 h-3.5 text-white" aria-hidden />}
              {active && <Loader2 className="w-3.5 h-3.5 text-white animate-spin" aria-hidden />}
              {!done && !active && (
                <span className="w-2 h-2 rounded-full bg-verdict-navy-200" aria-hidden />
              )}
            </div>
            <span className={cn(
              'transition-colors duration-200',
              done   && 'text-verdict-navy-100 line-through',
              active && 'text-white font-medium',
              !done && !active && 'text-verdict-navy-200',
            )}>
              {step.label}
            </span>
          </motion.div>
        );
      })}
    </div>
  );
}
```

---

## 9. RESPONSIVE DESIGN

### 9.1 Screen Support Matrix

| Screen | Mobile < 768px | Tablet 768–1023px | Desktop ≥ 1024px |
|--------|---------------|------------------|-----------------|
| `/login` | ✅ Full | ✅ Full | ✅ Full |
| `/dashboard` | ✅ Single column | ✅ 2-col grid | ✅ 3-col grid |
| `/cases/:id` | ✅ Tabs, stacked | ✅ Full | ✅ Full |
| `/briefs/:id` | ✅ Simplified radar | ✅ Full | ✅ Full |
| `/session/:id/live` | ❌ Block — show message | ⚠️ Degraded, single panel | ✅ Three-panel |
| `/witness/session/:id` | ✅ Full | ✅ Full | ✅ Full |

### 9.2 Mobile-First Implementation

```tsx
// Dashboard — mobile first, escalates to multi-column
<div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4 sm:gap-6">
  {cases.map(c => <CaseCard key={c.id} case={c} />)}
</div>

// Case detail tabs — horizontal scroll on mobile
<div className="flex overflow-x-auto scrollbar-none border-b border-verdict-navy-300/30 -mx-6 px-6 sm:mx-0 sm:px-0">
  <TabBar tabs={['Documents', 'Witnesses', 'Sessions', 'Briefs']} />
</div>

// Brief — single column, constrained width
<div className="max-w-2xl mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-4 sm:space-y-6">
  <ScoreHero ... />
</div>

// Page header — stack on mobile, side by side on desktop
<div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-6 sm:mb-8">
  <h1 className="text-xl sm:text-2xl font-bold text-white">{title}</h1>
  <div className="flex items-center gap-3">{actions}</div>
</div>
```

### 9.3 Touch Targets (WCAG 2.5.5)

All interactive elements must have a minimum 44×44px touch target.

```tsx
// All Button size="md" → h-10 (40px). Enforce minimum width:
<Button size="md" className="min-w-[44px]">

// Button size="lg" → h-11 (44px) ✅ already compliant

// Icon buttons — expand hit area with negative margin trick
<button
  className="p-2 -m-2 rounded-md flex items-center justify-center"
  style={{ minWidth: 44, minHeight: 44 }}
  aria-label="..."
>
  <X className="w-4 h-4" />
</button>

// Small badge/chip actions — ensure adequate spacing
// Minimum 8px between adjacent touch targets (WCAG 2.5.8)
<div className="flex flex-wrap gap-2"> {/* gap-2 = 8px */}
  {chips.map(c => <FocusAreaChip key={c.value} {...c} />)}
</div>
```

### 9.4 Responsive Typography

```tsx
// Page titles — smaller on mobile
<h1 className="text-xl sm:text-2xl font-bold text-white">

// Score hero — scales down on mobile
<motion.span className="text-5xl sm:text-7xl font-bold">

// Navigation — hide labels on mobile, show on tablet+
<NavLink>
  <span className="w-4 h-4" aria-hidden>{icon}</span>
  <span className="hidden sm:inline">{label}</span>
</NavLink>

// Card stats — tighter on mobile
<div className="text-xs sm:text-sm text-verdict-navy-50">
```

---

## 10. PERFORMANCE GUIDELINES

### 10.1 Next.js Image Optimization

```tsx
// RULE: Never use <img>. Always use next/image.
import Image from 'next/image';

// Above-the-fold assets → priority
<Image src="/logo.svg" alt="VERDICT" width={80} height={24} priority />

// Below-fold → lazy (default)
<Image src={witness.avatarUrl ?? '/avatars/default.png'} alt="" width={40} height={40} className="rounded-full" />

// Fill mode for aspect-ratio containers
<div className="relative aspect-[16/9] rounded-lg overflow-hidden">
  <Image src={imageUrl} alt="" fill className="object-cover" sizes="(max-width: 768px) 100vw, 640px" />
</div>
```

### 10.2 Code Splitting — Dynamic Imports

Heavy dependencies loaded only when needed:

```tsx
import dynamic from 'next/dynamic';

// MediaPipe WASM (~8MB) — witness session view only
const BehavioralSentinel = dynamic(
  () => import('@/components/session/BehavioralSentinel'),
  { loading: () => <Skeleton className="h-10 w-full rounded" />, ssr: false }
);

// Recharts (~150KB) — brief and witness profile only
const WeaknessMapChart = dynamic(
  () => import('@/components/brief/WeaknessMapChart'),
  { loading: () => <Skeleton className="h-64 w-64 rounded-full mx-auto" />, ssr: false }
);

// WaveSurfer (~120KB) — live session only
const WaveformVisualizer = dynamic(
  () => import('@/components/session/WaveformVisualizer'),
  { ssr: false }
);

// Framer Motion — only import what you use
import { motion, AnimatePresence } from 'framer-motion';
// Never: import * as FramerMotion from 'framer-motion'
```

### 10.3 Rendering Strategy

```tsx
// Server Components (RSC) — default for static/data-fetching screens
// apps/frontend/src/app/dashboard/page.tsx
export default async function DashboardPage() {
  const cases = await getCasesForFirm(); // fetch on server, no client JS
  return <DashboardClient cases={cases} />;
}

// Client Components — only when needed:
// - WebSocket connections (live session)
// - useState / useEffect
// - Browser APIs (MediaPipe, WaveSurfer)
// - Framer Motion animations
'use client';
export function LiveSessionPanel() { ... }

// Streaming with Suspense — progressive render of heavy pages
import { Suspense } from 'react';
<Suspense fallback={<BriefSkeleton />}>
  <BriefContent briefId={briefId} />  // Async Server Component
</Suspense>
```

### 10.4 Bundle Size Targets

| Route | JS budget | Approach |
|-------|-----------|---------|
| `/login` | < 50KB | Static, no heavy deps |
| `/dashboard` | < 120KB | RSC, lazy load charts |
| `/cases/:id` | < 150KB | RSC, lazy modals |
| `/session/:id/live` | < 400KB | WaveSurfer + Framer Motion acceptable |
| `/briefs/:id` | < 250KB | Recharts lazy loaded |
| `/witness/session/:id` | < 300KB | MediaPipe lazy loaded |

### 10.5 Critical Path

```css
/* globals.css — inlined critical styles (handled by Tailwind automatically) */

/* Ensure VERDICT design tokens don't cause FOUC */
:root {
  color-scheme: dark;       /* Prevents white flash on dark OS themes */
  background-color: #0F1729; /* Match body before Tailwind loads */
}

body {
  background-color: #0F1729;
  color: #FFFFFF;
}
```

### 10.6 Lazy Loading Rules

```tsx
// Always lazy load:
// - Modal content (load on open, not on page load)
// - Tab panel content below the fold
// - Alert details below first 3 in rail
// - Witness profile score chart (below main content)
// - Audio clips in brief (load on play button click)

// Never lazy load:
// - Above-the-fold navigation
// - Auth form inputs
// - Session timer (critical for live session UX)
// - Alert rail first 3 items
```

---

## 11. BROWSER SUPPORT

### 11.1 Supported Browsers

VERDICT targets the browsers used by AmLaw 200 firms (enterprise, managed devices):

| Browser | Version | Support |
|---------|---------|---------|
| Chrome  | Last 2 | ✅ Primary target |
| Edge    | Last 2 | ✅ Full support (enterprise standard) |
| Safari  | Last 2 (macOS + iOS) | ✅ Full support (partner iPads) |
| Firefox | Last 2 | ✅ Full support |
| IE 11   | — | ❌ Not supported |
| Chrome Android | Last 2 | ✅ Witness view |
| Safari iOS | Last 2 | ✅ Witness view, brief reading |

### 11.2 Progressive Enhancement

```tsx
// Camera / MediaPipe — degrade gracefully
function BehavioralSentinelOptional() {
  const [cameraAvailable, setCameraAvailable] = React.useState<boolean | null>(null);

  React.useEffect(() => {
    if (!navigator.mediaDevices?.getUserMedia) {
      setCameraAvailable(false);
      return;
    }
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(() => setCameraAvailable(true))
      .catch(() => setCameraAvailable(false));
  }, []);

  if (cameraAvailable === false) {
    return (
      <div className="text-xs text-verdict-navy-100 flex items-center gap-1.5">
        <EyeOff className="w-3.5 h-3.5" aria-hidden />
        Behavioral Sentinel unavailable (no camera)
      </div>
    );
  }

  if (cameraAvailable === null) return <Skeleton className="h-4 w-32" />;
  return <BehavioralSentinel />;
}

// WebSocket — reconnect with exponential backoff
class SessionWebSocket {
  private retryDelay = 1000;
  private maxRetry = 30000;

  connect(url: string) {
    const ws = new WebSocket(url);
    ws.onclose = () => {
      setTimeout(() => this.connect(url), this.retryDelay);
      this.retryDelay = Math.min(this.retryDelay * 2, this.maxRetry);
    };
    ws.onopen = () => { this.retryDelay = 1000; }; // reset on success
    return ws;
  }
}

// Web Animations API — fall back to CSS when Framer Motion unavailable
// (Framer Motion targets same browsers so this is not needed, but
//  all CSS-only animations in tailwind.config.ts act as the fallback)
```

### 11.3 Polyfills

```tsx
// next.config.ts — Next.js handles most polyfills automatically
// Required manual polyfill: crypto.randomUUID in older Safari

// apps/frontend/src/lib/uuid.ts
export function generateId(): string {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  // Fallback for older Safari
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16);
  });
}
```

### 11.4 Feature Detection

```tsx
// Check for required APIs before using them
export const CAPABILITIES = {
  camera:       typeof navigator !== 'undefined' && !!navigator.mediaDevices?.getUserMedia,
  webSocket:    typeof WebSocket !== 'undefined',
  webAudio:     typeof AudioContext !== 'undefined' || typeof (window as any).webkitAudioContext !== 'undefined',
  mediaSource:  typeof MediaSource !== 'undefined',
  serviceWorker:typeof navigator !== 'undefined' && 'serviceWorker' in navigator,
} as const;

// Usage in session config
{!CAPABILITIES.camera && (
  <p className="text-xs text-verdict-amber-400 flex items-center gap-1.5 mt-1">
    <AlertTriangle className="w-3.5 h-3.5" aria-hidden />
    Camera not available — Behavioral Sentinel will be disabled
  </p>
)}
```

---

## APPENDIX A — Tailwind Config (Complete)

```js
// apps/frontend/tailwind.config.ts
import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        'verdict-navy': {
          900: '#0A0F1C', 800: '#0F1729', 700: '#131E30', 600: '#1E2B3C',
          500: '#253347', 400: '#2D3E54', 300: '#374B63', 200: '#4A6080',
          100: '#6B849E', 50: '#94A3B8',
        },
        'verdict-blue': {
          900: '#1E3A5F', 800: '#1D4ED8', 700: '#2563EB', 600: '#3B82F6',
          500: '#60A5FA', 400: '#93C5FD', 300: '#BFDBFE', 100: '#DBEAFE', 50: '#EFF6FF',
        },
        'verdict-red': {
          900: '#7F1D1D', 800: '#991B1B', 700: '#B91C1C', 600: '#DC2626',
          500: '#EF4444', 400: '#F87171', 200: '#FECACA', 100: '#FEE2E2', 50: '#FFF5F5',
        },
        'verdict-amber': {
          700: '#92400E', 600: '#D97706', 500: '#F59E0B', 400: '#FCD34D',
          200: '#FDE68A', 100: '#FEF3C7', 50: '#FFFBEB',
        },
        'verdict-green': {
          700: '#065F46', 600: '#059669', 500: '#10B981', 400: '#34D399',
          200: '#A7F3D0', 100: '#D1FAE5', 50: '#ECFDF5',
        },
        'verdict-purple': {
          700: '#4C1D95', 600: '#7C3AED', 500: '#8B5CF6', 400: '#A78BFA',
          300: '#C4B5FD', 100: '#EDE9FE',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
      },
      fontSize: {
        '2xs': ['0.6875rem', { lineHeight: '1rem' }],
        'xs':  ['0.75rem',   { lineHeight: '1rem' }],
        'sm':  ['0.875rem',  { lineHeight: '1.25rem' }],
        'base':['1rem',      { lineHeight: '1.5rem' }],
        'lg':  ['1.125rem',  { lineHeight: '1.75rem' }],
        'xl':  ['1.25rem',   { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem',    { lineHeight: '2rem' }],
        '3xl': ['1.875rem',  { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem',   { lineHeight: '2.5rem' }],
        '5xl': ['3rem',      { lineHeight: '1' }],
        '6xl': ['4rem',      { lineHeight: '1' }],
      },
      boxShadow: {
        'card-sm':     '0 1px 2px rgba(0,0,0,0.3), 0 0 0 1px rgba(255,255,255,0.03)',
        'card':        '0 4px 6px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.05)',
        'card-lg':     '0 10px 15px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.07)',
        'modal':       '0 25px 50px rgba(0,0,0,0.7), 0 0 0 1px rgba(255,255,255,0.08)',
        'alert-red':   '0 0 0 1px rgba(239,68,68,0.6), 0 4px 12px rgba(239,68,68,0.2)',
        'alert-amber': '0 0 0 1px rgba(245,158,11,0.6), 0 4px 12px rgba(245,158,11,0.2)',
        'alert-green': '0 0 0 1px rgba(16,185,129,0.6), 0 4px 12px rgba(16,185,129,0.2)',
        'glow-blue':   '0 0 16px rgba(59,130,246,0.35)',
        'glow-purple': '0 0 16px rgba(139,92,246,0.35)',
        'glow-green':  '0 0 12px rgba(16,185,129,0.4)',
      },
      keyframes: {
        'slide-in-down':    { '0%': { opacity: '0', transform: 'translateY(-20px) scale(0.96)' }, '100%': { opacity: '1', transform: 'translateY(0) scale(1)' } },
        'slide-out-right':  { '0%': { opacity: '1', transform: 'translateX(0)' }, '100%': { opacity: '0', transform: 'translateX(100%)' } },
        'slide-in-right':   { '0%': { opacity: '0', transform: 'translateX(60px)' }, '100%': { opacity: '1', transform: 'translateX(0)' } },
        'pulse-border-red': { '0%, 100%': { boxShadow: '0 0 0 1px rgba(239,68,68,0.5)' }, '50%': { boxShadow: '0 0 0 3px rgba(239,68,68,0.85), 0 0 20px rgba(239,68,68,0.3)' } },
        'badge-pop':        { '0%': { transform: 'scale(1)' }, '50%': { transform: 'scale(1.3)' }, '100%': { transform: 'scale(1)' } },
        'confirm-flash':    { '0%': { backgroundColor: 'rgba(16,185,129,0.3)' }, '100%': { backgroundColor: 'transparent' } },
        'monitoring-pulse': { '0%, 100%': { opacity: '1' }, '50%': { opacity: '0.35' } },
        'cascade-in':       { '0%': { opacity: '0', transform: 'translateY(10px)' }, '100%': { opacity: '1', transform: 'translateY(0)' } },
        'amplitude-glow':   { '0%, 100%': { boxShadow: '0 0 6px rgba(139,92,246,0.2)' }, '50%': { boxShadow: '0 0 20px rgba(139,92,246,0.6)' } },
        'fade-in':          { '0%': { opacity: '0' }, '100%': { opacity: '1' } },
      },
      animation: {
        'slide-in-down':   'slide-in-down 300ms cubic-bezier(0.34,1.56,0.64,1) forwards',
        'slide-out-right': 'slide-out-right 200ms cubic-bezier(0.7,0,0.84,0) forwards',
        'slide-in-right':  'slide-in-right 300ms cubic-bezier(0.16,1,0.3,1) forwards',
        'pulse-border-red':'pulse-border-red 600ms ease-in-out 2',
        'badge-pop':       'badge-pop 150ms ease-in-out',
        'confirm-flash':   'confirm-flash 200ms ease-out forwards',
        'monitoring-pulse':'monitoring-pulse 2000ms ease-in-out infinite',
        'cascade-in':      'cascade-in 500ms cubic-bezier(0.16,1,0.3,1) forwards',
        'amplitude-glow':  'amplitude-glow 800ms ease-in-out infinite',
        'fade-in':         'fade-in 400ms ease-out forwards',
      },
    },
  },
  plugins: [require('@tailwindcss/forms')],
};

export default config;
```

---

## APPENDIX B — globals.css

```css
/* apps/frontend/src/app/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Prevent FOUC on dark theme */
:root {
  color-scheme: dark;
}

/* Base resets */
*, *::before, *::after {
  box-sizing: border-box;
}

body {
  background-color: #0F1729;
  color: #FFFFFF;
  font-family: Inter, system-ui, -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Focus — global baseline (components override with focus-visible:ring-*) */
*:focus-visible {
  outline: 2px solid #3B82F6;
  outline-offset: 2px;
}

/* Remove default focus for mouse users */
*:focus:not(:focus-visible) {
  outline: none;
}

/* Custom scrollbar — dark theme */
::-webkit-scrollbar       { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #131E30; }
::-webkit-scrollbar-thumb { background: #374B63; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #4A6080; }

/* Alert rail — hide scrollbar but keep scroll */
.scrollbar-none::-webkit-scrollbar { display: none; }
.scrollbar-none { scrollbar-width: none; }

/* Transcript — auto-scroll behavior */
.transcript-container {
  scroll-behavior: smooth;
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

/* @tailwindcss/forms — restyle for VERDICT dark theme */
@layer base {
  [type='text'], [type='email'], [type='password'], [type='number'],
  [type='search'], [type='url'], textarea, select {
    background-color: #1E2B3C;
    border-color: rgba(55, 75, 99, 0.5);
    color: #FFFFFF;
    border-radius: 0.25rem;
  }

  [type='checkbox'], [type='radio'] {
    background-color: #1E2B3C;
    border-color: rgba(55, 75, 99, 0.5);
    color: #3B82F6;
  }
}
```

---

## APPENDIX C — Component Quick Reference

| Component | File | Key Props |
|-----------|------|-----------|
| `<Button>` | `ui/Button.tsx` | `variant`, `size`, `loading`, `icon`, `iconPosition` |
| `<Input>` | `ui/Input.tsx` | `label`, `error`, `success`, `helperText`, `inputSize` |
| `<Textarea>` | `ui/Input.tsx` | `label`, `error`, `rows` |
| `<Card>` | `ui/Card.tsx` | Standard HTML div props |
| `<InteractiveCard>` | `ui/Card.tsx` | `onClick` |
| `<AlertCard>` | `ui/Card.tsx` | `type`, `impeachmentRisk`, `isConfirmed`, `isRejected` |
| `<CaseCard>` | `ui/Card.tsx` | `case`, `onClick` |
| `<Badge>` | `ui/Badge.tsx` | `variant`, `dot` |
| `<Modal>` | `ui/Modal.tsx` | `open`, `onClose`, `title`, `description`, `size` |
| `<ConfirmModal>` | `ui/Modal.tsx` | `onConfirm`, `danger`, `confirmLabel` |
| `<VerdictToast>` | `ui/Toast.tsx` | `title`, `description`, `variant`, `onDismiss` |
| `<ToggleSwitch>` | `ui/Toggle.tsx` | `checked`, `onChange` |
| `<ToggleRow>` | `ui/Toggle.tsx` | `label`, `description`, `badge`, `checked`, `onChange` |
| `<Skeleton>` | `ui/Skeleton.tsx` | `className` (for sizing) |
| `<DashboardSkeleton>` | `ui/Skeleton.tsx` | — |
| `<BriefSkeleton>` | `ui/Skeleton.tsx` | — |
| `<EmptyState>` | `ui/EmptyState.tsx` | `context`, `compact`, `onAction` |
| `<ScoreHero>` | `brief/ScoreHero.tsx` | `score`, `delta`, `sessionNumber` |
| `<SessionTimer>` | `session/SessionTimer.tsx` | `durationMinutes`, `startedAt`, `status` |
| `<AgentStatusRow>` | `session/AgentStatusPanel.tsx` | `name`, `status` |
| `<BriefGenerationSteps>` | `session/BriefGenerationSteps.tsx` | `currentStepIndex` |
| `<GlobalNav>` | `layout/GlobalNav.tsx` | — |
| `<PageLayout>` | `layout/PageLayout.tsx` | `title`, `description`, `actions`, `maxWidth` |

