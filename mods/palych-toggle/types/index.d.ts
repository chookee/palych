export type PalychToggleMode = boolean
export type PalychTheme = 'dark' | 'light'

declare module 'claude-code' {
  interface PluginState {
    'palych-toggle': {
      isOn: PalychToggleMode
      isOnPending: boolean
      theme: PalychTheme
    }
  }
}
