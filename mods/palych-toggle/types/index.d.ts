export type PalychToggleMode = boolean

declare module 'claude-code' {
  interface PluginState {
    'palych-toggle': { isOn: PalychToggleMode; isOnPending: boolean }
  }
}
