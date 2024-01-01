import { Controller } from '@hotwired/stimulus'
import { connectStreamSource, disconnectStreamSource } from '@hotwired/turbo'

export default class extends Controller {
  es: EventSource | null = null

  declare urlValue: string
  static values = {
    url: String,
  }

  connect(): void {
    this.es = new EventSource(this.urlValue)
    connectStreamSource(this.es)
  }

  disconnect(): void {
    if (this.es) {
      this.es.close()
      disconnectStreamSource(this.es)
    }
  }
}
