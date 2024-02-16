import { Controller } from '@hotwired/stimulus'

export default class extends Controller<HTMLElement> {
  declare readonly menuTarget: HTMLDivElement
  static targets = ['menu']

  hide(): void {
    this.menuTarget.classList.add('hidden')
  }

  show(): void {
    this.menuTarget.classList.remove('hidden')
  }
}
