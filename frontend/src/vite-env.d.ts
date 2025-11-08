/// <reference types="vite/client" />

declare namespace JSX {
  interface IntrinsicElements {
    'elevenlabs-convai': {
      'agent-id': string
      style?: React.CSSProperties
      children?: React.ReactNode
      [key: string]: any
    }
  }
}
