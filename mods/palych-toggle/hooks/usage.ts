// Usage figures for the band: the 5h and 7d limits and the context window.
// The drawing is ported from usage-band (https://github.com/JetsonChan/CC-Usage-Band,
// commit 60cd609), MIT License, Copyright (c) 2026 Jetson Chan, without its shine
// animation and cache hit figure. Keeping the figures current follows usage-line
// (https://github.com/sundyme/usage-line, commit 194c8f7), MIT License,
// Copyright (c) 2026 sundyme.
import { atom, read, update } from 'claude-code'
import type { EngineInterface, On } from 'claude-code'

import type { Ctx, Limit, Style } from '../types'

const now = atom({ plugin: 'palych-toggle', key: 'now' } as const, 0)
const ctx = atom({ plugin: 'palych-toggle', key: 'ctx' } as const, null as Ctx | null)
const limits = atom({ plugin: 'palych-toggle', key: 'limits' } as const, [] as Limit[])
const style = atom({ plugin: 'palych-toggle', key: 'style' } as const, 'unicode' as Style)

const MINUTE = 60_000
// Cells between figures, so each group reads apart from its neighbours.
export const GROUP_GAP = 4

// ---- Data

type Measure = { context: Ctx; rateLimits: Limit[] }
export type Usage = { m: Measure | null; at: number; s: Style }

export async function readUsage($: EngineInterface): Promise<Usage> {
  const c = await read($, ctx)
  const rl = await read($, limits)
  const at = await read($, now)
  const s = await read($, style)
  const m = c === null && rl.length === 0 ? null : { context: c ?? { window: 0 }, rateLimits: rl }
  return { m, at, s }
}

export async function startUsage($: EngineInterface) {
  // Glyphs and figures are read apart, so a failed lookup of one keeps the other.
  try {
    const icons = ((await $.env.get('USAGE_BAND_ICONS')) ?? 'auto').trim().toLowerCase() || 'auto'
    const term = await $.env.get('TERM_PROGRAM')
    await update($, style, () => detectStyle(icons, term))
  } catch {}
  try {
    const u = await $.session.usage()
    await update($, ctx, () => u.context)
    if (u.rateLimits.length) await update($, limits, () => u.rateLimits)
    const t0 = await $.clock.now()
    await update($, now, () => t0)
  } catch {}

  // Once a minute, for the reset countdowns: the band redraws on every write.
  $.clock.every(MINUTE, async () => {
    try {
      const t = await $.clock.now()
      await update($, now, () => t)
      // Refill figures the session dropped (a /clear goes on under a new session id).
      const u = await $.session.usage()
      if (u.rateLimits.length && !(await read($, limits)).length) await update($, limits, () => u.rateLimits)
      if ((await read($, ctx)) === null) await update($, ctx, () => u.context)
    } catch {}
  })
}

export const registerUsage = (on: On) => {
  on('session.measure', async ($, e, next) => {
    try {
      if (e.changed.includes('context')) await update($, ctx, () => e.context)
      if (e.rateLimits.length && e.changed.includes('rateLimits')) await update($, limits, () => e.rateLimits)
    } catch {}
    return next(e)
  })

  // A /clear or compaction changes the context fill.
  on('classic.SessionStart', async ($, e, next) => {
    const r = await next(e)
    try {
      if (e.source === 'clear' || e.source === 'compact') {
        const u = await $.session.usage()
        await update($, ctx, () => u.context)
      }
    } catch {}
    return r
  })
}

// ---- Shared

// One hue per metric; RED takes over only when a metric is in trouble
const HUE = { five: '#5cc4d6', seven: '#e8a25f', ctx: '#9aa5f5' }
const RED = '#e5685f'
const TRACK = '#4a4f5c'

const GLYPHS: Record<Style, { ctx: string; fill: string; track: string }> = {
  nerd: { ctx: '\u{F0328} ', fill: '■', track: '■' },
  unicode: { ctx: '≡ ', fill: '■', track: '■' },
  ascii: { ctx: 'ctx ', fill: '#', track: '-' },
}

// Terminals known to ship Nerd Font symbols without the user installing a font
const NERD_BUILTIN = new Set(['ghostty'])

const detectStyle = (setting: string, termProgram: string | undefined): Style => {
  if (setting === 'nerd' || setting === 'unicode' || setting === 'ascii') return setting
  return NERD_BUILTIN.has((termProgram ?? '').toLowerCase()) ? 'nerd' : 'unicode'
}

const fmtTokens = (n: number): string => {
  if (n >= 1_000_000) return `${+(n / 1_000_000).toFixed(n >= 10_000_000 ? 0 : 1)}M`
  if (n >= 1_000) return `${+(n / 1_000).toFixed(n >= 100_000 ? 0 : 1)}K`
  return String(n)
}

const fmtLeft = (ms: number): string => {
  const mins = Math.max(0, Math.round(ms / MINUTE))
  const d = Math.floor(mins / 1440)
  const h = Math.floor((mins % 1440) / 60)
  const m = mins % 60
  if (d > 0) return `${d}d${h}h`
  if (h > 0) return `${h}h${m}m`
  return `${m}m`
}

// A window whose reset has passed starts over at zero until the next reading.
const usedPct = (l: Limit, at: number) =>
  l.resetsAt && Date.parse(l.resetsAt) <= at ? 0 : Math.round(l.percentUsed)
const leftText = (l: Limit, at: number) =>
  l.resetsAt && Date.parse(l.resetsAt) > at ? fmtLeft(Date.parse(l.resetsAt) - at) : ''

// Blend a #rrggbb color toward white (t > 0) or black (t < 0) by |t|
const lighten = (hex: string, t: number): string => {
  const n = parseInt(hex.slice(1), 16)
  const target = t >= 0 ? 255 : 0
  const ch = (v: number) => Math.round(v + (target - v) * Math.abs(t)).toString(16).padStart(2, '0')
  return `#${ch((n >> 16) & 255)}${ch((n >> 8) & 255)}${ch(n & 255)}`
}

const limitsOf = (m: Measure | null) => [
  { label: '5h', name: '5-hour limit', hue: HUE.five, l: m?.rateLimits.find(l => l.kind === 'five_hour') },
  { label: '7d', name: '7-day limit', hue: HUE.seven, l: m?.rateLimits.find(l => l.kind === 'seven_day') },
]

// ---- Terminal: one row of colored spans

export type Span = { text: string; color?: string; dim?: boolean }

const SEP: Span = { text: ' '.repeat(GROUP_GAP) }

const width = (spans: Span[]) => spans.reduce((n, s) => n + [...s.text].length, 0)

// A bar whose filled part runs from a deep shade of its color to a bright one
const bar = (pct: number, cells: number, color: string, s: Style): Span[] => {
  const g = GLYPHS[s]
  const filled = Math.max(pct > 0 ? 1 : 0, Math.min(cells, Math.round((pct / 100) * cells)))
  const spans: Span[] = []
  for (let i = 0; i < filled; i++) {
    const shade = filled === 1 ? 0 : -0.15 + (0.35 * i) / (filled - 1)
    spans.push({ text: g.fill, color: lighten(color, shade) })
  }
  if (cells > filled) spans.push({ text: g.track.repeat(cells - filled), color: TRACK })
  return spans
}

// detail 2: bars + countdowns; 1: no bars; 0: bare numbers
const layout = ({ m, at, s }: Usage, detail: 0 | 1 | 2): Span[] => {
  const g = GLYPHS[s]
  const groups: Span[][] = []

  for (const { label, hue, l } of limitsOf(m)) {
    if (!l) continue
    const pct = usedPct(l, at)
    const color = pct >= 80 ? RED : hue
    const out: Span[] = [{ text: `${label} `, color }]
    if (detail === 2) out.push(...bar(pct, 8, color, s), { text: ' ' })
    out.push({ text: `${pct}%`, color })
    const left = leftText(l, at)
    if (detail >= 1 && left) out.push({ text: ` · ${left}`, dim: true })
    groups.push(out)
  }

  if (m && m.context.window) {
    const pct = m.context.percent ?? 0
    const color = pct >= 80 ? RED : HUE.ctx
    groups.push([
      { text: g.ctx, color },
      { text: fmtTokens(m.context.tokens ?? 0), color },
      { text: `/${fmtTokens(m.context.window)}`, dim: true },
    ])
  }

  return groups.flatMap((grp, i) => (i === 0 ? grp : [SEP, ...grp]))
}

export const fit = (u: Usage, cols: number) =>
  ([2, 1, 0] as const).map(d => layout(u, d)).find(spans => width(spans) <= cols) ?? layout(u, 0)

// ---- Desktop: each group is one SVG drawn as a plain image, so the groups can wrap
// under each other on a narrow band.

const esc = (v: string) => v.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

// CAP: the band the figures' cap height occupies (Inter 13px on baseline 19.5);
// icons, dots and the inner rule are sized to it so the row reads one height
const CAP = { top: 9.75, h: 10 }
export const D = { h: 30, inner: 7, barW: 76, barH: 6 }
const FONT = 13
// Advance widths in em for Inter with tabular figures (SF Pro, the fallback, runs within a few %).
// Each text also sets textLength to this width, so a font that runs wider or narrower only
// changes letter spacing and never pushes into the next element.
const ADVANCE: Record<string, number> = { h: 0.58, d: 0.6, m: 0.9, K: 0.64, M: 0.84, '%': 0.84, '/': 0.36, '.': 0.27, ' ': 0.26 }
// Extra space between letters, in px; textLength spreads it evenly across each string
const TRACKING = 0.2
const textW = (v: string, size: number) =>
  [...v].reduce((w, c) => w + (c >= '0' && c <= '9' ? 0.62 : (ADVANCE[c] ?? 0.6)), 0) * size +
  TRACKING * Math.max(0, [...v].length - 1)

// Text tinted toward the hue: deeper on light backgrounds, lighter on dark ones
const pinW = (v: string, size: number) => `textLength="${textW(v, size).toFixed(1)}" lengthAdjust="spacing"`
const ink = (hue: string, x: number, y: number, v: string, size: number) =>
  `<text x="${x}" y="${y}" font-size="${size}" ${pinW(v, size)} class="ink" style="--l:${lighten(hue, -0.38)};--d:${lighten(hue, 0.25)}">${esc(v)}</text>`
const mute = (x: number, y: number, v: string, size: number) =>
  `<text x="${x}" y="${y}" font-size="${size}" ${pinW(v, size)} class="mute">${esc(v)}</text>`

type Group = { width: number; body: string }
// Each group starts 1px into its picture.
const X = 1

// 5h ▬▬▬▬▬▬──── 69% │ 1h31m: label, bar, figure, then when it resets
const limitGroup = (label: string, l: Limit, hue: string, at: number): Group => {
  const pct = usedPct(l, at)
  const color = pct >= 80 ? RED : hue
  const pctText = `${pct}%`
  const left = leftText(l, at)
  const labelW = textW(label, FONT) + D.inner
  const pctW = textW(pctText, FONT)
  const width = labelW + D.barW + D.inner + pctW + (left ? D.inner * 2 + 1 + textW(left, FONT) : 0)
  const fillW = Math.max(pct > 0 ? D.barH : 0, Math.min(D.barW, (D.barW * pct) / 100))
  const bx = X + labelW
  const y = (D.h - D.barH) / 2
  const r = D.barH / 2
  const px = bx + D.barW + D.inner
  const out = [
    `<rect x="${bx}" y="${y}" width="${D.barW}" height="${D.barH}" rx="${r}" class="track" style="--h:${color}"/>`,
    `<rect x="${bx}" y="${y}" width="${fillW}" height="${D.barH}" rx="${r}" fill="${lighten(color, -0.12)}"/>`,
    ink(color, X, 19.5, label, FONT),
    ink(color, px, 19.5, pctText, FONT),
  ]
  if (left) {
    const rx = px + pctW + D.inner
    out.push(`<rect x="${rx}" y="${CAP.top}" width="1" height="${CAP.h}" class="rule"/>`, mute(rx + 1 + D.inner, 19.5, left, FONT))
  }
  return { width, body: out.join('') }
}

// Three stacked sheets: the context window, drawn in a CAP.h square, outer stroke edge included
const layersIcon = (color: string) =>
  `<g fill="none" stroke="${color}" stroke-width="1.2" stroke-linejoin="round">` +
  `<path d="M5 0.6 L9.4 2.8 L5 5 L0.6 2.8 Z" fill="${color}" fill-opacity="0.25"/>` +
  `<path d="M0.6 5.2 L5 7.4 L9.4 5.2"/><path d="M0.6 7.2 L5 9.4 L9.4 7.2"/></g>`

// Context as a 2×10 dot matrix: one dot per 1/20 of the window (50K of 1M), filling the top
// row left to right before the bottom one.
// Rows sit so the dots' outer edges meet the CAP band: CAP.top + r and CAP.top + CAP.h - r
const DOTS = { cols: 10, pitch: 5, r: 1.6, rows: [11.35, 18.15] }
const ctxGroup = (hue: string, tokens: number, window: number, pct: number): Group => {
  const lit = Math.min(DOTS.cols * 2, Math.round((pct / 100) * DOTS.cols * 2))
  const num = fmtTokens(tokens)
  const suffix = `/${fmtTokens(window)}`
  const lw = CAP.h + 6
  const matrixW = DOTS.cols * DOTS.pitch
  const mx = X + lw
  const dot = (i: number) =>
    `<circle cx="${mx + DOTS.pitch / 2 + (i % DOTS.cols) * DOTS.pitch}" cy="${DOTS.rows[Math.floor(i / DOTS.cols)]}" r="${DOTS.r}"/>`
  const on = Array.from({ length: lit }, (_, i) => dot(i)).join('')
  const off = Array.from({ length: DOTS.cols * 2 - lit }, (_, i) => dot(lit + i)).join('')
  const nx = mx + matrixW + D.inner
  return {
    width: lw + matrixW + D.inner + textW(num, FONT) + 1 + textW(suffix, FONT),
    body:
      `<g transform="translate(${X} ${CAP.top})">${layersIcon(lighten(hue, -0.15))}</g>` +
      `<g class="track" style="--h:${hue}">${off}</g>` +
      `<g fill="${lighten(hue, -0.12)}">${on}</g>` +
      ink(hue, nx, 19.5, num, FONT) +
      mute(nx + textW(num, FONT) + 1, 19.5, suffix, FONT),
  }
}

// An image takes its color scheme from the app; declaring both schemes lets it follow the
// app and stay transparent.
const SVG_HEAD =
  `<style>` +
  `:root{color-scheme:light dark;background:transparent}` +
  `text{font-family:Inter,"SF Pro Text",system-ui,-apple-system,"Segoe UI",sans-serif;font-weight:500;font-feature-settings:"tnum","cv05"}` +
  `.track{fill:var(--h);fill-opacity:.22}` +
  `.ink{fill:var(--l)}.mute{fill:#8b8f97;font-weight:400}.rule{fill:#000;fill-opacity:.1}` +
  `@media (prefers-color-scheme:dark){.ink{fill:var(--d)}.mute{fill:#9aa0a8}.rule{fill:#fff;fill-opacity:.13}}` +
  `</style>`

const wrap = (width: number, body: string) =>
  `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${D.h}" viewBox="0 0 ${width} ${D.h}" style="color-scheme:light dark;background:transparent">${SVG_HEAD}${body}</svg>`

export type Part = { key: string; svg: string; width: number; alt: string }

export const desktopParts = ({ m, at }: Usage): Part[] => {
  const groups: { key: string; g: Group; alt: string }[] = []
  for (const { label, name, hue, l } of limitsOf(m)) {
    if (!l) continue
    const left = leftText(l, at)
    groups.push({
      key: label,
      g: limitGroup(label, l, hue, at),
      alt: `${name} ${usedPct(l, at)}% used${left ? `, resets in ${left}` : ''}`,
    })
  }
  if (m && m.context.window) {
    const pct = m.context.percent ?? 0
    groups.push({
      key: 'ctx',
      g: ctxGroup(pct >= 80 ? RED : HUE.ctx, m.context.tokens ?? 0, m.context.window, pct),
      alt: `context ${fmtTokens(m.context.tokens ?? 0)} of ${fmtTokens(m.context.window)}`,
    })
  }
  return groups.map(({ key, g, alt }) => {
    const width = Math.ceil(g.width + 2)
    return { key, svg: wrap(width, g.body), width, alt }
  })
}
