import { expect, mock, test } from 'claude-code/testing'
import type { Engine } from 'claude-code/testing'
import type { On } from 'claude-code'

const BAND = {
  hasSurvey: false,
  isWorking: false,
  maxRows: 10,
  bodyColumns: 80,
  scroll: { offset: 0, bodyRows: 10 },
  view: {},
} as const

type Node = { props: Record<string, unknown> }
type Band = {
  find: (query: { type?: string; key?: string; text?: string }) => Promise<Node | undefined>
  findAll: (query: { type?: string }) => Promise<Node[]>
}

// What the switch shows: the pill's alt on the desktop, the dot in the terminal.
const shown = async (band: Band, surface: 'terminal' | 'desktop') => {
  if (surface === 'desktop') {
    const alts = (await band.findAll({ type: 'Svg' })).map(n => String(n.props.alt))
    return alts.find(alt => alt.startsWith('Палыч'))
  }
  const label = (await band.find({ key: 'palych-toggle' }))?.props.label

  return label === '●' ? 'Палыч вкл' : label === '○' ? 'Палыч выкл' : undefined
}

for (const surface of ['terminal', 'desktop'] as const) {
  test(`${surface}: the switch flips the label and the model's note`, async ($, on) => {
    const seen: (readonly string[] | undefined)[] = []
    on('prompt.submit', (_, e) => {
      seen.push(e.context)

      return { text: e.text }
    })

    const band = await $.ui.mount({
      plugin: 'palych-toggle',
      surface,
      component: 'AbovePrompt',
      props: BAND,
    })
    expect((await band.find({ type: 'Text', text: 'Палыч' }))?.type).toBe('Text')
    expect(await shown(band, surface)).toBe('Палыч вкл')

    await $.prompt.submit({ text: 'привет' })
    expect(seen.at(-1)).toBe(undefined)

    await band.press({ key: 'palych-toggle' })
    expect(await shown(band, surface)).toBe('Палыч выкл')

    await $.prompt.submit({ text: 'привет' })
    expect(seen.at(-1)?.at(-1)).toContain('Palych is OFF')
    await $.prompt.submit({ text: 'ещё' })
    expect(seen.at(-1)?.at(-1)).toContain('Palych is OFF')

    await band.press({ key: 'palych-toggle' })
    expect(await shown(band, surface)).toBe('Палыч вкл')

    await $.prompt.submit({ text: 'привет' })
    expect(seen.at(-1)?.at(-1)).toContain('Palych is ON again')
    await $.prompt.submit({ text: 'ещё' })
    expect(seen.at(-1)).toBe(undefined)
  })

  test(`${surface}: a typed control phrase moves the switch`, async ($, on) => {
    const seen: (readonly string[] | undefined)[] = []
    on('prompt.submit', (_, e) => {
      seen.push(e.context)

      return { text: e.text }
    })

    const band = await $.ui.mount({
      plugin: 'palych-toggle',
      surface,
      component: 'AbovePrompt',
      props: BAND,
    })

    await $.prompt.submit({ text: 'Отключи Палыча.' })
    expect(seen.at(-1)).toBe(undefined)
    expect(await shown(band, surface)).toBe('Палыч выкл')

    await $.prompt.submit({ text: 'Turn off palych and explain why' })
    expect(seen.at(-1)?.at(-1)).toContain('Palych is OFF')

    await $.prompt.submit({ text: 'Включи Палыча' })
    expect(seen.at(-1)).toBe(undefined)
    expect(await shown(band, surface)).toBe('Палыч вкл')
  })

  test(`${surface}: a survey keeps the band`, async ($, on) => {
    on('ui.render', ($, e) => {
      const { Box } = $.ui.resolve(e)

      return <Box key="engine" />
    })

    const band = await $.ui.mount({
      plugin: 'palych-toggle',
      surface,
      component: 'AbovePrompt',
      props: { ...BAND, hasSurvey: true },
    })
    expect(await band.find({ key: 'palych-toggle' })).toBe(undefined)
  })
}

const MIN = 60_000
const HOUR = 60 * MIN
const T0 = Date.parse('2026-10-04T12:00:00.000Z')

// The engine beneath the mod: usage readings and the clock.
const world = async ($: Engine, on: On) => {
  on('session.measure', (_, e) => ({ changed: e.changed }))
  on('command.register', (_, e) => ({ value: { command: e.name } }))
  const clock = mock.clock(on, { now: T0 })
  const usage = {
    startedAt: T0,
    context: { window: 200_000, tokens: 50_000, percent: 25 },
    rateLimits: [
      { kind: 'five_hour', percentUsed: 12.5, resetsAt: new Date(T0 + 2 * HOUR + 54 * MIN).toISOString() },
      { kind: 'seven_day', percentUsed: 63, resetsAt: new Date(T0 + 101 * HOUR).toISOString() },
    ],
  }
  on('session.usage', () => ({ value: usage }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  await $.session.start({ cwd: '/tmp', surface: 'desktop', isInteractive: true })
  return clock
}

const band = async ($: Engine, surface: 'terminal' | 'desktop', bodyColumns = 120) => {
  const ui = await $.ui.mount({ plugin: 'palych-toggle', surface, component: 'AbovePrompt', props: { ...BAND, bodyColumns } })
  const texts = (await ui.findAll({ type: 'Text' })).map(t => t.text)
  const alts = (await ui.findAll({ type: 'Svg' })).map(n => String(n.props.alt))
  const tree = JSON.stringify(await ui.drawn())
  await ui.unmount()
  return { texts, alts, tree }
}

test('desktop: the switch comes first, then 5h, 7d and ctx', async ($, on) => {
  await world($, on)
  const { texts, alts } = await band($, 'desktop')
  expect(texts).toEqual(['Палыч'])
  expect(alts).toEqual([
    'Палыч вкл',
    '5-hour limit 13% used, resets in 2h54m',
    '7-day limit 63% used, resets in 4d5h',
    'context 50K of 200K',
  ])
})

test('the reset countdown moves with the clock', async ($, on) => {
  const clock = await world($, on)
  await clock.advance(MIN)
  expect((await band($, 'desktop')).alts[1]).toBe('5-hour limit 13% used, resets in 2h53m')
})

test('desktop: only the figures wrap, never the switch', async ($, on) => {
  await world($, on)
  const { tree } = await band($, 'desktop', 30)
  expect(tree.match(/"flexWrap":"wrap"/g)?.length).toBe(1)
})

test('terminal: bars give way first on a narrow band', async ($, on) => {
  await world($, on)
  const wide = (await band($, 'terminal', 80)).texts
  expect(wide[0]).toBe('Палыч')
  expect(wide).toContain('13%')
  expect(wide).toContain(' · 2h54m')
  expect(wide).toContain('/200K')
  expect(wide.some(t => t?.includes('■'))).toBe(true)
  const narrow = (await band($, 'terminal', 60)).texts
  expect(narrow).toContain(' · 2h54m')
  expect(narrow.some(t => t?.includes('■'))).toBe(false)
})

for (const surface of ['terminal', 'desktop'] as const) {
  test(`${surface}: /palych-tab hides the band and brings it back`, async ($, on) => {
    // The engine's own band, drawn while Palych's is hidden.
    on('ui.render', ($, e) => {
      const { Box } = $.ui.resolve(e)

      return <Box key="engine" />
    })
    await world($, on)
    const ui = await $.ui.mount({ plugin: 'palych-toggle', surface, component: 'AbovePrompt', props: BAND })
    expect(await ui.find({ key: 'palych-toggle' })).not.toBe(undefined)

    expect((await $.command.run({ command: 'palych-tab' })).text).toBe('Панель Палыча скрыта')
    expect(await ui.find({ key: 'palych-toggle' })).toBe(undefined)

    expect((await $.command.run({ command: 'palych-tab' })).text).toBe('Панель Палыча показана')
    expect(await ui.find({ key: 'palych-toggle' })).not.toBe(undefined)
  })
}
