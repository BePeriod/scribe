import { Controller } from '@hotwired/stimulus'

export class LanguageToggleController extends Controller<HTMLElement> {
  declare readonly checkboxInputTarget: HTMLInputElement
  declare readonly btnTarget: HTMLButtonElement
  declare readonly switchBackgroundTarget: HTMLSpanElement
  declare readonly switchForegroundTarget: HTMLSpanElement
  static targets = ['checkboxInput', 'btn', 'switchBackground', 'switchForeground']

  declare readonly languageToggleOutlets: LanguageToggleController[]
  static outlets = ['language-toggle']

  initialize(): void {
    if (this.checkboxInputTarget.checked) {
      this.applyEnabledStyles()
    } else {
      this.applyDisabledStyles()
    }
  }

  applyEnabledStyles(): void {
    this.switchBackgroundTarget.classList.remove('bg-gray-200')
    this.switchBackgroundTarget.classList.add('bg-emerald-600')
    this.switchForegroundTarget.classList.remove('translate-x-0')
    this.switchForegroundTarget.classList.add('translate-x-5')
  }

  applyDisabledStyles(): void {
    this.switchBackgroundTarget.classList.remove('bg-emerald-600')
    this.switchBackgroundTarget.classList.add('bg-gray-200')
    this.switchForegroundTarget.classList.remove('translate-x-5')
    this.switchForegroundTarget.classList.add('translate-x-0')
  }

  enable(): void {
    this.applyEnabledStyles()
    this.checkboxInputTarget.checked = true
  }

  disable(): void {
    this.applyDisabledStyles()
    this.checkboxInputTarget.checked = false
  }

  toggle(): void {
    if (this.checkboxInputTarget.checked) {
      this.disable()
    } else {
      this.enable()
    }
  }

  toggleAll(): void {
    if (this.checkboxInputTarget.checked) {
      this.disable()
      this.languageToggleOutlets.forEach((outlet) => {
        outlet.disable()
      })
    } else {
      this.enable()
      this.languageToggleOutlets.forEach((outlet) => {
        outlet.enable()
      })
    }
  }
}
