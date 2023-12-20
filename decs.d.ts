declare module '@hotwired/turbo' {
  export const connectStreamSource: (es: EventSource) => void
  export const disconnectStreamSource: (es: EventSource) => void
}
