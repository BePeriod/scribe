import { Controller } from '@hotwired/stimulus'

export default class extends Controller<HTMLFormElement> {
  reset(): void {
    this.element.reset()
  }
}
