from nicegui import ui

# Shared chart palette (purple-first, matches the editorial theme)
CHART_COLORS = [
    '#cba6f7', '#8a5ce8', '#89b4fa', '#4d6be8', '#f9e2af',
    '#6fcf7c', '#f38ba8', '#e8b34d', '#a79fc0', '#74c7ec',
]

METRIC_VALUE_CLASSES = {
    'primary': 'text-white',
    'secondary': 'oy-text-accent',
    'accent': 'oy-text-blue',
    'info': 'oy-text-blue',
    'positive': 'oy-text-green',
}

GLOBAL_CSS = """
<style>
:root {
  --oy-bg: #0a0912;
  --oy-surface: rgba(255,255,255,.035);
  --oy-surface-2: rgba(255,255,255,.06);
  --oy-border: rgba(255,255,255,.08);
  --oy-border-soft: rgba(255,255,255,.07);
  --oy-text: #f5f2fb;
  --oy-body-text: #c9c1de;
  --oy-muted: #8f89a3;
  --oy-faint: #726d84;
  --oy-soft: #a79fc0;
  --oy-placeholder: #4c465e;
  --oy-accent: #cba6f7;
  --oy-accent-deep: #8a5ce8;
  --oy-blue: #89b4fa;
  --oy-green: #6fcf7c;
  --oy-red: #f38ba8;
  --oy-yellow: #f9e2af;
  --oy-gold: #e8b34d;
  --oy-ink: #14101d;
  --oy-font-display: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --oy-font-body: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --oy-font-mono: ui-monospace, "SFMono-Regular", Consolas, "Liberation Mono", monospace;
}

/* ---------- Base canvas ---------- */
body, body.body--dark {
  background: radial-gradient(1100px 560px at 88% -8%, #2a1d42 0%, #0a0912 55%) fixed var(--oy-bg) !important;
  font-family: var(--oy-font-body);
  color: var(--oy-body-text);
}
.q-layout, .q-page-container, .q-page { background: transparent !important; }

a { color: var(--oy-accent); }
a:hover { color: #e6d9fb; }

::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,.14);
  border-radius: 999px;
  border: 2px solid transparent;
  background-clip: content-box;
}
::-webkit-scrollbar-thumb:hover { background-color: rgba(255,255,255,.25); }

/* ---------- Typography ---------- */
.text-h3, .text-h4, .text-h5 {
  font-family: var(--oy-font-display);
  font-weight: 700;
  color: var(--oy-text);
  letter-spacing: -.3px;
}
.text-h4 { font-size: 2.1rem; line-height: 1.1; }
.text-h5 { font-size: 1.6rem; line-height: 1.15; }
.text-h6 {
  font-family: var(--oy-font-display);
  font-weight: 600;
  color: var(--oy-text);
  letter-spacing: .2px;
}

.oy-h1 {
  font-family: var(--oy-font-display);
  font-size: 2.35rem;
  font-weight: 700;
  line-height: 1.05;
  letter-spacing: -.3px;
  color: var(--oy-text);
}
.oy-sub { font-size: 13px; color: var(--oy-muted); }
.oy-label {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  color: var(--oy-muted);
}
.oy-stat {
  font-family: var(--oy-font-display);
  font-size: 2.1rem;
  font-weight: 700;
  line-height: 1.1;
  color: var(--oy-text);
}
.oy-mono { font-family: var(--oy-font-mono); }
.oy-display { font-family: var(--oy-font-display); letter-spacing: -.2px; }
.oy-seclabel {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  color: var(--oy-blue);
}

/* ---------- Surfaces ---------- */
.q-card, .q-card--dark {
  background: var(--oy-surface);
  border: 1px solid var(--oy-border);
  border-radius: 14px;
  box-shadow: none;
  color: var(--oy-body-text);
}
.oy-card {
  background: var(--oy-surface);
  border: 1px solid var(--oy-border);
  border-radius: 14px;
}
.collection-card { overflow: hidden; border-radius: 10px; }

/* Legacy utility remaps: old pages use gray-* utilities everywhere */
.bg-dark { background: var(--oy-surface) !important; }
.bg-gray-900, .bg-gray-950 { background: rgba(255,255,255,.03) !important; }
.bg-gray-800 { background: rgba(255,255,255,.06) !important; }
.bg-gray-700 { background: rgba(255,255,255,.09) !important; }
.border-gray-600, .border-gray-700, .border-gray-800 { border-color: var(--oy-border) !important; }
.hover\\:bg-gray-800:hover, .hover\\:bg-gray-700:hover { background: rgba(255,255,255,.05) !important; }
.hover\\:border-gray-500:hover, .hover\\:border-gray-600:hover { border-color: rgba(203,166,247,.45) !important; }
.text-gray-300 { color: var(--oy-body-text) !important; }
.text-gray-400, .text-gray-600, .text-grey-4, .text-grey-5 { color: var(--oy-muted) !important; }
.text-gray-500, .text-grey-6 { color: var(--oy-faint) !important; }

/* Semantic accent remaps: set codes gold, prices green, warnings soft */
.text-yellow-500, .text-orange-400 { color: var(--oy-gold) !important; }
.text-yellow-400 { color: var(--oy-yellow) !important; }
.text-green-400, .text-green-500 { color: var(--oy-green) !important; }
.text-red-400, .text-red-500 { color: var(--oy-red) !important; }
.text-blue-300, .text-blue-400 { color: var(--oy-blue) !important; }
.text-purple-400 { color: var(--oy-accent) !important; }
.font-mono { font-family: var(--oy-font-mono) !important; }

/* Semantic utility classes for Python-rendered elements */
.oy-text-accent { color: var(--oy-accent) !important; }
.oy-text-blue { color: var(--oy-blue) !important; }
.oy-text-green { color: var(--oy-green) !important; }
.oy-text-gold { color: var(--oy-gold) !important; }
.oy-text-body { color: var(--oy-body-text) !important; }
.oy-text-muted { color: var(--oy-muted) !important; }
.oy-text-faint { color: var(--oy-faint) !important; }
.oy-text-soft { color: var(--oy-soft) !important; }
.oy-text-placeholder { color: var(--oy-placeholder) !important; }
.oy-interactive-muted { color: var(--oy-muted) !important; }
.oy-interactive-muted:hover { color: var(--oy-text) !important; }
.oy-accent-border-hover:hover { border-color: rgba(203,166,247,.45) !important; }
.oy-metric-card:hover { border-color: rgba(203,166,247,.4) !important; }
.oy-nav-card:hover { border-color: rgba(203,166,247,.45) !important; }
.oy-nav-glow { background: rgba(203,166,247,.1); }
.oy-nav-card:hover .oy-nav-glow { background: rgba(203,166,247,.2); }
.oy-nav-card:hover .oy-nav-card-title { color: var(--oy-accent) !important; }
.oy-add-storage:hover { border-color: rgba(203,166,247,.6) !important; }
.oy-add-storage:hover .oy-add-storage-icon { color: var(--oy-accent) !important; }
.oy-add-storage:hover .oy-add-storage-label { color: var(--oy-text) !important; }

.q-separator { background: rgba(255,255,255,.08) !important; }

/* ---------- Buttons ---------- */
.q-btn {
  font-family: var(--oy-font-body);
  font-weight: 600;
  letter-spacing: .2px;
  text-transform: none;
}
.q-btn--rectangle { border-radius: 999px; }
.q-btn.bg-secondary, .q-btn.bg-accent,
.q-btn.bg-positive, .q-btn.bg-negative, .q-btn.bg-info, .q-btn.bg-warning {
  color: var(--oy-ink) !important;
}
.q-btn.bg-primary { color: var(--oy-text) !important; }
.q-btn.bg-green { background: var(--oy-green) !important; color: var(--oy-ink) !important; }
.q-btn.bg-red { background: var(--oy-red) !important; color: var(--oy-ink) !important; }
.q-btn.bg-orange { background: var(--oy-gold) !important; color: var(--oy-ink) !important; }

.q-btn.bg-purple { background: var(--oy-accent-deep) !important; color: #fff !important; }
.q-btn.bg-blue { background: var(--oy-blue) !important; color: var(--oy-ink) !important; }

/* ---------- Uploader (drop zones) ---------- */
.q-uploader {
  background: rgba(255,255,255,.03);
  border: 1px dashed rgba(255,255,255,.18);
  border-radius: 12px;
  box-shadow: none;
}
.q-uploader__header {
  background: transparent;
  color: var(--oy-body-text);
}
.q-uploader__list { background: transparent; }

/* Chips on light accent backgrounds need dark ink text */
.q-chip.bg-secondary, .q-chip.bg-accent,
.q-chip.bg-positive, .q-chip.bg-warning {
  color: var(--oy-ink) !important;
}
.q-chip.bg-primary { color: var(--oy-text) !important; }
.q-chip.bg-primary .q-icon { color: var(--oy-text) !important; }
.q-chip.bg-secondary .q-icon,
.q-chip.bg-accent .q-icon, .q-chip.bg-positive .q-icon, .q-chip.bg-warning .q-icon {
  color: var(--oy-ink) !important;
}

/* ---------- Fields ---------- */
.q-field__control {
  background: rgba(255,255,255,.04);
  border-radius: 10px;
  box-shadow: inset 0 0 0 1px var(--oy-border);
  padding: 0 12px;
}
.q-field--standard .q-field__control:before,
.q-field--standard .q-field__control:after { display: none; }
.q-field--outlined .q-field__control:before,
.q-field--outlined .q-field__control:after { border: none; }
.q-field--focused .q-field__control { box-shadow: inset 0 0 0 1px rgba(203,166,247,.6); }
.q-field__native, .q-field__input, .q-field__prefix, .q-field__suffix {
  color: var(--oy-text) !important;
  font-family: var(--oy-font-body);
}
.q-field__label { color: var(--oy-muted); }
.q-field__marginal { color: var(--oy-muted); }

/* ---------- Tables ---------- */
.q-table__container {
  background: var(--oy-surface) !important;
  border: 1px solid var(--oy-border);
  border-radius: 12px;
}
.q-table thead th {
  font-size: 10.5px;
  font-weight: 600;
  letter-spacing: .8px;
  text-transform: uppercase;
  color: var(--oy-faint);
}
.q-table tbody td { color: var(--oy-body-text); }
.q-table tbody tr:hover { background: rgba(255,255,255,.03); }
.q-table__bottom { color: var(--oy-muted); }

/* ---------- Tabs ---------- */
.q-tab {
  text-transform: none;
  font-family: var(--oy-font-body);
  font-weight: 600;
  letter-spacing: .2px;
  color: var(--oy-muted);
}
.q-tab--active { color: var(--oy-accent); }
.q-tab__indicator { background: var(--oy-accent); }

/* ---------- Overlays ---------- */
.q-dialog .q-card, .q-menu {
  background: #171321;
  border: 1px solid rgba(255,255,255,.1);
  backdrop-filter: blur(12px);
}
.q-menu { border-radius: 12px; color: var(--oy-body-text); }
.q-item__label { color: var(--oy-body-text); }
.q-item--active, .q-manual-focusable--focused { color: var(--oy-accent); }
.q-tooltip {
  background: #241c3a;
  color: #ecdffb;
  border-radius: 8px;
  font-family: var(--oy-font-body);
}
.q-notification { border-radius: 12px; font-family: var(--oy-font-body); }

/* ---------- Single-card views ---------- */
.oy-single-card-dialog,
.q-dialog .q-card.oy-single-card-dialog {
  background:
    radial-gradient(900px 520px at 5% 8%, rgba(138,92,232,.16), transparent 62%),
    linear-gradient(135deg, #0d0b17 0%, #12101d 48%, #0a0912 100%);
  border: 0;
  border-radius: 0;
  color: var(--oy-body-text);
}
.oy-single-card-shell { background: transparent; }
.oy-single-card-art {
  background:
    radial-gradient(circle at 50% 42%, rgba(203,166,247,.13), transparent 42%),
    linear-gradient(155deg, rgba(255,255,255,.035), rgba(0,0,0,.2));
  border-right: 1px solid var(--oy-border);
  overflow: hidden;
}
.oy-single-card-art::after {
  content: '';
  position: absolute;
  inset: 9%;
  border: 1px solid rgba(203,166,247,.08);
  border-radius: 24px;
  pointer-events: none;
}
.oy-single-card-image {
  z-index: 1;
  border-radius: 10px;
  filter: drop-shadow(0 24px 38px rgba(0,0,0,.52));
}
.oy-single-card-content { background: transparent; }
.oy-single-card-close {
  background: rgba(10,9,18,.72) !important;
  border: 1px solid rgba(255,255,255,.12);
  color: var(--oy-soft) !important;
  backdrop-filter: blur(10px);
  transition: background .15s, border-color .15s, color .15s;
}
.oy-single-card-close:hover {
  background: rgba(203,166,247,.14) !important;
  border-color: rgba(203,166,247,.42);
  color: var(--oy-text) !important;
}
.oy-single-card-title {
  font-family: var(--oy-font-display);
  color: var(--oy-text);
  font-weight: 700;
  line-height: 1.08;
  letter-spacing: -.45px;
}
.oy-single-card-meta {
  font-family: var(--oy-font-mono);
  color: var(--oy-faint);
  font-size: 11px;
}
.oy-single-card-panel,
.q-card.oy-single-card-panel {
  background: rgba(255,255,255,.032);
  border: 1px solid var(--oy-border);
  border-radius: 14px;
  box-shadow: none;
}
.oy-single-card-stat {
  min-width: 0;
  padding: 13px 14px;
  gap: 4px;
  background: rgba(255,255,255,.028);
  border: 1px solid rgba(255,255,255,.065);
  border-radius: 11px;
}
.oy-single-card-stat-label {
  color: var(--oy-muted);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 1.1px;
  line-height: 1.2;
  text-transform: uppercase;
}
.oy-single-card-stat-value {
  color: var(--oy-text);
  font-family: var(--oy-font-display);
  font-size: 17px;
  font-weight: 600;
  line-height: 1.25;
  overflow-wrap: anywhere;
}
.oy-single-card-effect {
  color: var(--oy-body-text);
  font-size: 16px;
  line-height: 1.72;
}
.oy-single-card-status .q-chip {
  background: rgba(203,166,247,.11) !important;
  border: 1px solid rgba(203,166,247,.2);
  color: #e8def7 !important;
}
.oy-single-card-status .q-chip .q-icon { color: var(--oy-accent) !important; }
.oy-single-card-owned {
  color: var(--oy-accent);
  font-family: var(--oy-font-display);
  font-weight: 700;
}
.oy-single-card-inventory,
.q-card.oy-single-card-inventory { background: rgba(203,166,247,.035); }
.oy-single-card-set-list { overflow: hidden; }
.oy-single-card-set-header {
  background: rgba(203,166,247,.07);
  border-bottom: 1px solid var(--oy-border);
  color: var(--oy-muted);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 1px;
  text-transform: uppercase;
}
.oy-single-card-set-row {
  border-bottom: 1px solid rgba(255,255,255,.055);
  color: var(--oy-body-text);
}
.oy-single-card-set-row:last-child { border-bottom: 0; }
.oy-single-card-set-row:hover { background: rgba(255,255,255,.025); }
.oy-single-card-chart {
  background: rgba(255,255,255,.02);
  border: 1px solid var(--oy-border);
  border-radius: 12px;
  overflow: hidden;
}
.oy-single-card-table-header { background: rgba(203,166,247,.07); }
.oy-single-card-table-row {
  border-bottom: 1px solid rgba(255,255,255,.055);
  transition: background .15s;
}
.oy-single-card-table-row:hover { background: rgba(203,166,247,.055); }

@media (max-width: 639px) {
  .oy-single-card-art {
    border-right: 0;
    border-bottom: 1px solid var(--oy-border);
  }
  .oy-single-card-art::after { inset: 6%; }
}

/* ---------- Shell (drawer + header) ---------- */
.q-drawer {
  background: rgba(15,13,24,.85);
  border-right: 1px solid var(--oy-border-soft);
  backdrop-filter: blur(12px);
}
.q-header {
  background: rgba(10,9,18,.75);
  border-bottom: 1px solid var(--oy-border-soft);
  backdrop-filter: blur(12px);
}

.oy-logo {
  font-family: var(--oy-font-display);
  font-size: 19px;
  font-weight: 600;
  letter-spacing: .3px;
  color: #f4f1fa;
}
.oy-navlabel {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 1.6px;
  color: #6d6784;
  padding: 0 12px;
}
.oy-navrow {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  color: var(--oy-muted);
  cursor: pointer;
  transition: background .15s, color .15s;
}
.oy-navrow:hover { color: #ecdffb; background: rgba(255,255,255,.04); }
.oy-navrow.active {
  background: linear-gradient(90deg, rgba(203,166,247,.16), rgba(203,166,247,.02));
  color: #ecdffb;
}
.oy-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--oy-accent);
  box-shadow: 0 0 8px var(--oy-accent);
  flex: none;
}
</style>
"""


def apply_theme():
    """Applies the global color theme and editorial design system."""
    ui.colors(
        primary='#1e1e2e',   # Dark background
        secondary='#cba6f7', # Accent purple
        accent='#89b4fa',    # Accent blue
        dark='#12101a',      # Dark surface
        positive='#6fcf7c',  # Green
        negative='#f38ba8',  # Red
        info='#89b4fa',      # Blue
        warning='#f9e2af'    # Yellow
    )
    # Force dark mode for the page
    ui.dark_mode().enable()


def install_global_styles() -> None:
    """Install the design system once for all NiceGUI pages."""
    ui.add_head_html(GLOBAL_CSS, shared=True)


def page_header(title: str, subtitle: str | None = None):
    """Standard oversized editorial page heading."""
    header = ui.column().classes('gap-1')
    with header:
        ui.label(title).classes('oy-h1')
        if subtitle:
            ui.label(subtitle).classes('oy-sub')
    return header
