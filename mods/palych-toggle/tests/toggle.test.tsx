import { expect, test } from 'claude-code/testing'

const BAND = {
  hasSurvey: false,
  isWorking: false,
  maxRows: 10,
  bodyColumns: 80,
  scroll: { offset: 0, bodyRows: 10 },
  view: {},
} as const

type Band = {
  find: (query: { type?: string; key?: string; text?: string }) => Promise<
    { props: Record<string, unknown> } | undefined
  >
}

// What the switch shows: the pill's alt on the desktop, the dot in the terminal.
const shown = async (band: Band, surface: 'terminal' | 'desktop') => {
  if (surface === 'desktop') {
    return (await band.find({ type: 'Svg' }))?.props.alt
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
