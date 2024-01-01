import { Controller } from '@hotwired/stimulus'

export default class extends Controller<HTMLElement> {
  readonly entering = ['transform', 'ease-out', 'duration-300', 'transition']
  readonly enterFrom = ['translate-y-2', 'opacity-0', 'sm:translate-y-0', 'sm:translate-x-2']
  readonly enterTo = ['translate-y-0', 'opacity-100', 'sm:translate-x-0']

  readonly leaving = ['transition', 'ease-in', 'duration-100']
  readonly leavingFrom = ['opacity-100']
  readonly leavingTo = ['opacity-0']

  connect() {
    this.element.classList.remove(...this.enterFrom)
    this.element.classList.add(...this.enterTo)
  }

  disconnect() {
    this.element.classList.remove(...this.entering)
    this.element.classList.add(...this.leaving)
    this.element.classList.remove(...this.leavingFrom)
    this.element.classList.add(...this.leavingTo)
  }
}
