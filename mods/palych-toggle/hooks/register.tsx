import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

// Session state: Palych starts on in every new conversation, as its rules do.
const isOn = atom({ plugin: 'palych-toggle', key: 'isOn' } as const, true)
// Set when the switch turns Palych back on; the next prompt tells the model once.
const isOnPending = atom(
  { plugin: 'palych-toggle', key: 'isOnPending' } as const,
  false,
)

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

    const { Box, Button, Text } = $.ui.resolve(e)
    const active = await read($, isOn)

    const toggle = async () => {
      await update($, isOn, value => !value)
      // Only a switch back on after an off needs a one-time note.
      await update($, isOnPending, () => !active)
    }

    return (
      <Box>
        <Text color={active ? 'green' : undefined} dimColor={!active}>
          {active ? 'Палыч вкл' : 'Палыч выкл'}{' '}
        </Text>
        <Button
          key="palych-toggle"
          label={active ? 'Выключить' : 'Включить'}
          onPress={toggle}
        />
      </Box>
    )
  })
}
