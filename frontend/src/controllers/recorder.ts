import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  stream: MediaStream | null = null
  recorder: MediaRecorder | null = null
  audioChunks: Blob[] = []
  audioRecording: Blob | null = null

  declare permissionGrantedValue: boolean
  static values = {
    permissionGranted: { type: Boolean, default: false },
  }

  declare readonly btnTarget: HTMLButtonElement
  declare readonly disabledIconTarget: SVGElement
  declare readonly playIconTarget: SVGElement
  declare readonly stopIconTarget: SVGElement
  declare readonly loadingIconTarget: SVGElement
  declare readonly audioInputTarget: HTMLInputElement
  static targets = ['btn', 'disabledIcon', 'playIcon', 'stopIcon', 'loadingIcon', 'audioInput']

  async initialize(): Promise<void> {
    if (
      navigator /* eslint-disable-line @typescript-eslint/no-unnecessary-condition -- linter reads this as always truthy */
        ?.mediaDevices /* eslint-disable-line @typescript-eslint/no-unnecessary-condition -- linter reads this as always truthy */
        ?.getUserMedia /* eslint-disable-line @typescript-eslint/no-unnecessary-condition -- linter reads this as always truthy */
    ) {
      try {
        this.stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        this.recorder = new MediaRecorder(this.stream)
        this.permissionGrantedValue = true

        this.recorder.ondataavailable = (event) => {
          this.audioChunks.push(event.data)
        }

        this.recorder.onstart = () => {
          this.showIcon('stop')
        }

        this.recorder.onstop = () => {
          this.showIcon('play')

          this.audioRecording = new Blob(this.audioChunks, {
            type: 'audio/ogg; codecs=opus',
          })

          this.uploadRecording()

          this.audioChunks = []
        }
      } catch (error) {
        console.error('Error accessing media devices:', error)
      }
    } else {
      console.error('Audio recording is not supported')
    }
  }

  permissionGrantedValueChanged(): void {
    this.btnTarget.disabled = !this.permissionGrantedValue
    if (this.permissionGrantedValue) {
      this.showIcon('play')
    } else {
      this.showIcon('disabled')
    }
  }

  toggle(): void {
    console.log('toggle', this.recorder)
    if (this.recorder?.state === 'recording') {
      this.recorder.stop()
    } else {
      this.recorder?.start()
    }
  }

  uploadRecording(): void {
    if (this.audioRecording) {
      this.showIcon('loading')
      try {
        const file = new File([this.audioRecording], 'recording.ogg', {
          type: 'audio/ogg',
          lastModified: new Date().getTime(),
        })
        const container = new DataTransfer()
        container.items.add(file)
        this.audioInputTarget.files = container.files

        this.audioInputTarget.form?.requestSubmit()
      } catch (error) {
        console.error('request failed', error)
      } finally {
        this.showIcon('play')
      }
    }
  }

  showIcon(icon: 'disabled' | 'play' | 'stop' | 'loading'): void {
    Object.entries({
      disabled: this.disabledIconTarget,
      play: this.playIconTarget,
      stop: this.stopIconTarget,
      loading: this.loadingIconTarget,
    }).forEach(([key, el]) => {
      if (key === icon) {
        el.classList.remove('hidden')
      } else {
        el.classList.add('hidden')
      }
    })
  }
}
