import { Controller } from '@hotwired/stimulus'

export default class extends Controller<HTMLElement> {
  declare readonly hiddenInputTarget: HTMLInputElement
  declare readonly filterInputTarget: HTMLInputElement
  declare readonly listboxTarget: HTMLUListElement
  declare readonly optionTargets: HTMLLIElement[]
  static targets = ['hiddenInput', 'filterInput', 'listbox', 'option']

  declare channelValue: string
  static values = {
    channel: String,
  }

  activeOptionIndex = -1
  activeOption?: HTMLLIElement
  visibleOptions: HTMLLIElement[] = []

  initialize(): void {
    this.filterOptions()

    this.optionTargets.forEach((option, index) => {
      if (option.dataset.active === 'true') {
        this.activeOptionIndex = index
        this.activeOption = option
      }
    })
  }

  toggle(): void {
    const hidden = this.listboxTarget.className.includes('hidden')
    if (hidden) {
      this.listboxTarget.classList.remove('hidden')
    } else {
      this.listboxTarget.classList.add('hidden')
    }
  }

  filter(): void {
    this.listboxTarget.classList.remove('hidden')
    this.filterOptions()
  }

  filterOptions(): void {
    this.visibleOptions = []
    this.activeOptionIndex = -1
    this.optionTargets.forEach((option, index) => {
      if (
        option
          .getAttribute('data-channel-name')
          ?.toLowerCase()
          .includes(this.filterInputTarget.value.toLowerCase())
      ) {
        option.classList.remove('hidden')
        if (option.dataset.channelId) {
          this.visibleOptions.push(option)
          if (option === this.activeOption) {
            this.activeOptionIndex = index
          }
        }
      } else {
        option.classList.add('hidden')
      }
    })
  }

  select(event: Event): void {
    const option = event.currentTarget as HTMLLIElement
    const channelId = option.dataset.channelId
    const channelName = option.dataset.channelName

    this.hiddenInputTarget.value = channelId ?? ''
    this.filterInputTarget.value = channelName ?? ''
    this.channelValue = channelName ?? ''
    this.listboxTarget.classList.add('hidden')
    this.setActive(option)
  }

  selectActive(event: Event): void {
    event.preventDefault()
    if (this.activeOption) {
      const option = this.activeOption
      const channelId = option.dataset.channelId
      const channelName = option.dataset.channelName

      this.hiddenInputTarget.value = channelId ?? ''
      this.filterInputTarget.value = channelName ?? ''
      this.channelValue = channelName ?? ''
      this.listboxTarget.classList.add('hidden')
    }
  }

  setActive(target?: HTMLLIElement): void {
    this.optionTargets.forEach((option, index) => {
      if (option === target) {
        option.dataset.active = 'true'
        this.activeOptionIndex = index
        this.activeOption = option
      } else {
        option.dataset.active = 'false'
      }
    })
  }

  reset(event: FocusEvent): void {
    const related = event.relatedTarget as HTMLElement | null
    if (related instanceof HTMLLIElement && this.optionTargets.includes(related)) {
      const channelId = related.dataset.channelId
      const channelName = related.dataset.channelName

      this.hiddenInputTarget.value = channelId ?? ''
      this.filterInputTarget.value = channelName ?? ''
      this.channelValue = channelName ?? ''
      this.listboxTarget.classList.add('hidden')
      this.setActive(related)
    }
    this.filterInputTarget.value = this.channelValue
    this.listboxTarget.classList.add('hidden')
  }

  prev(): void {
    if (this.activeOptionIndex <= 0) {
      this.activeOptionIndex = 0
    } else {
      this.activeOptionIndex--
    }

    this.setActive(this.visibleOptions[this.activeOptionIndex])
  }

  next(): void {
    if (this.activeOptionIndex >= this.visibleOptions.length - 1) {
      this.activeOptionIndex = this.visibleOptions.length - 1
    } else {
      this.activeOptionIndex++
    }

    this.setActive(this.visibleOptions[this.activeOptionIndex])
  }

  clickOutside(event: Event): void {
    const target = event.target as HTMLElement | null

    if (!this.listboxTarget.contains(target)) {
      this.listboxTarget.classList.add('hidden')
    }
  }
}
