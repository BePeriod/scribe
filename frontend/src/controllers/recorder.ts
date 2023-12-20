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
  static targets = ['btn', 'disabledIcon', 'playIcon', 'stopIcon', 'loadingIcon']

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

        this.recorder.onstop = async () => {
          this.showIcon('play')

          this.audioRecording = new Blob(this.audioChunks, {
            type: 'audio/ogg; codecs=opus',
          })

          await this.uploadRecording()

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
    console.log('permission change')
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
      console.log('stopping recording')
      this.recorder.stop()
    } else {
      console.log('starting recording')
      this.recorder?.start()
    }
  }

  async uploadRecording(): Promise<void> {
    if (this.audioRecording) {
      this.showIcon('loading')
      try {
        const response = await window.fetch('/api/v1/upload', {
          method: 'POST',
          body: this.audioRecording,
          headers: {
            'Content-Type': 'audio/ogg',
          },
        })

        console.log('uploaded', response)
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
