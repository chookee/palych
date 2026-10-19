import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { PalychTheme } from '../types'

// Session state: Palych starts on in every new conversation, as its rules do.
const isOn = atom({ plugin: 'palych-toggle', key: 'isOn' } as const, true)
// Set when the switch turns Palych back on; the next prompt tells the model once.
const isOnPending = atom(
  { plugin: 'palych-toggle', key: 'isOnPending' } as const,
  false,
)

// The desktop app's theme, so the switch matches the band it sits on.
const theme = atom(
  { plugin: 'palych-toggle', key: 'theme' } as const,
  'dark' as PalychTheme,
)

// The switch and its theme handling follow the auto-compact switch of the
// usage-quota mod (MIT, (c) 2026 Anant Raghunath).
const PALETTES = {
  dark: { off: '#4b5163', on: '#4ade80', lit: '#8b919c', muted: '#8b90a0' },
  light: { off: '#b4b9c4', on: '#22c55e', lit: '#c3c7cf', muted: '#5b6070' },
}
// The pill in pixels; the light under the pointer shows in the PAD around it.
const SWITCH_W = 30
const SWITCH_H = 20
const SWITCH_PAD = 3
// Cells the switch's box takes, so the press's tint can't spill onto the label.
const SWITCH_CELLS = 4
// The box behind the switch is a pixel off the drawing; centre the pill in it.
const SWITCH_NUDGE = 0.5
// Lowercase text sits below the cell's middle; drop the pill 1px to meet it.
const SWITCH_DROP = 1
// Fully see-through: the unlit border and the press's own hover tint.
const CLEAR = '#00000000'

const switchSvg = (active: boolean, fill: string): string => {
  const w = SWITCH_W - 2 * SWITCH_PAD
  const tall = SWITCH_H - 2 * SWITCH_PAD
  const p = SWITCH_PAD
  const knob = p + (active ? w - tall / 2 : tall / 2)

  return (
    `<svg xmlns="http://www.w3.org/2000/svg" width="${SWITCH_W}" height="${SWITCH_H}" viewBox="${-SWITCH_NUDGE} ${-SWITCH_NUDGE - SWITCH_DROP} ${SWITCH_W} ${SWITCH_H}">` +
    `<rect x="${p}" y="${p}" width="${w}" height="${tall}" rx="${tall / 2}" fill="${fill}"/>` +
    `<circle cx="${knob}" cy="${p + tall / 2}" r="${tall / 2 - 2}" fill="#ffffff"/></svg>`
  )
}

// Plugins aren't told the app's theme: read it from the app's settings
// (userThemeMode) and, for "system", from the OS.
const THEME_EVERY_MS = 2_000

const desktopConfig = async ($: EngineInterface): Promise<string | undefined> => {
  const appData = await $.env.get('APPDATA')
  if (appData) {
    return `${appData}/Claude/config.json`
  }
  const home = await $.env.get('HOME')

  return home ? `${home}/Library/Application Support/Claude/config.json` : undefined
}

const osTheme = async ($: EngineInterface): Promise<PalychTheme> => {
  try {
    if (await $.env.get('APPDATA')) {
      const { stdout } = await $.process.run(
        ['reg', 'query', 'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize', '/v', 'AppsUseLightTheme'],
        { timeoutMs: 5_000 },
      )
      return /AppsUseLightTheme\s+REG_DWORD\s+0x1\b/.test(stdout) ? 'light' : 'dark'
    }
    const { stdout } = await $.process.run(
      ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
      { timeoutMs: 5_000 },
    )
    return /dark/i.test(stdout) ? 'dark' : 'light'
  } catch {
    // macOS has no AppleInterfaceStyle in light mode; unknown stays dark.
    return 'dark'
  }
}

// Read the settings file again only when it changed since the last look.
let themeFile: { mtimeMs: number; mode: string | undefined } | undefined

const syncTheme = async ($: EngineInterface): Promise<void> => {
  let mode: string | undefined
  try {
    const path = await desktopConfig($)
    if (!path) {
      return
    }
    const { mtimeMs } = await $.fs.stat(path)
    if (themeFile?.mtimeMs === mtimeMs) {
      mode = themeFile.mode
    } else {
      mode = (JSON.parse(await $.fs.read(path)) as { userThemeMode?: string }).userThemeMode
      themeFile = { mtimeMs, mode }
    }
  } catch {
    return
  }
  const value = mode === 'light' || mode === 'dark' ? mode : await osTheme($)
  if (value !== (await read($, theme))) {
    await update($, theme, () => value)
  }
}

// Whole-message control phrases, the same list the Palych session hook reads.
const PHRASES: Record<string, boolean> = {
  'включи палыча': true,
  'включи палыча для этого разговора': true,
  'включи палыча всегда': true,
  'отключи палыча': false,
  'отключи постоянное включение палыча': false,
  'включи palych': true,
  'включи palych для этого разговора': true,
  'включи palych всегда': true,
  'отключи palych': false,
  'отключи постоянное включение palych': false,
  'enable palych': true,
  'enable palych for this conversation': true,
  'enable palych always': true,
  'turn off palych': false,
  'disable palych always-on': false,
}

const SOURCE =
  'Palych toggle (the user set it with the switch in the app; not typed in this message): '
const OFF_NOTE =
  SOURCE +
  'Palych is OFF for this conversation. Treat this as the user\'s explicit request to turn Palych off: do not apply Palych\'s reply rules until the switch turns it on again.'
const ON_NOTE =
  SOURCE +
  'Palych is ON again for this conversation. Apply Palych\'s reply rules from the instructions.'

const phraseMode = (text: string): boolean | undefined => {
  const phrase = text.trim().toLowerCase().replace(/\.$/, '')

  return PHRASES[phrase]
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const result = await next(e)
    await syncTheme($)
    $.clock.every(THEME_EVERY_MS, () => void syncTheme($))

    return result
  })

  on('prompt.submit', async ($, e, next) => {
    if (e.command || e.isMeta) {
      return next(e)
    }

    // A typed control phrase speaks for itself; keep the switch in step with it.
    const typed = phraseMode(e.text)
    if (typed !== undefined) {
      await update($, isOn, () => typed)
      await update($, isOnPending, () => false)

      return next(e)
    }

    let note: string | undefined
    if (!(await read($, isOn))) {
      note = OFF_NOTE
    } else if (await read($, isOnPending)) {
      note = ON_NOTE
      await update($, isOnPending, () => false)
    }

    if (note === undefined) {
      return next(e)
    }

    return next({ ...e, context: [...(e.context ?? []), note] })
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey) {
      return next(e)
    }

    const table = $.ui.resolve(e)
    const { Box, Button, Text } = table
    const Svg = e.surface === 'desktop' && 'Svg' in table ? table.Svg : undefined
    const colors = PALETTES[Svg ? await read($, theme) : 'dark']
    const active = await read($, isOn)

    const toggle = async () => {
      await update($, isOn, value => !value)
      // Only a switch back on after an off needs a one-time note.
      await update($, isOnPending, () => !active)
    }

    return (
      // The label, then the switch, pressed to the right edge of the band.
      <Box
        flexDirection="row"
        alignItems="center"
        justifyContent="flex-end"
        columnGap={1}
        width="100%"
      >
        <Text color={active ? undefined : colors.muted}>Палыч</Text>
        {Svg ? (
          <Box key="switch" width={SWITCH_CELLS} height={1} overflow="hidden">
            {/* Three layers of one size share a centre: the light, the pill, the press. */}
            <Box
              position="absolute"
              top={0}
              left={0}
              width={SWITCH_CELLS}
              height={1}
              borderStyle="round"
              borderColor={CLEAR}
              hover={{ backgroundColor: colors.lit, borderColor: colors.lit }}
            />
            <Box
              position="absolute"
              top={0}
              left={0}
              width={SWITCH_CELLS}
              height={1}
              alignItems="center"
              justifyContent="center"
            >
              <Svg
                alt={active ? 'Палыч вкл' : 'Палыч выкл'}
                source={switchSvg(active, active ? colors.on : colors.off)}
                width={SWITCH_W}
                height={SWITCH_H}
              />
            </Box>
            <Box position="absolute" top={0} left={0}>
              <Button
                key="palych-toggle"
                label={'   '}
                plain
                hover={{ backgroundColor: CLEAR }}
                onPress={toggle}
              />
            </Box>
          </Box>
        ) : (
          <Button key="palych-toggle" label={active ? '●' : '○'} plain onPress={toggle} />
        )}
      </Box>
    )
  })
}
