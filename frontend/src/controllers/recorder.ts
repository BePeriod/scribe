import { Controller } from '@hotwired/stimulus'
import * as Turbo from '@hotwired/turbo'

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
        Turbo.visit(
          "/notify?type=error&title=Error%20accessing%20media%20devices&message=Scribe%20could%20not%access%20you're%20microphone"
        )
      }
    } else {
      Turbo.visit(
        "/notify?type=error&title=Audio%recording%is%20not%20supported&message=You're%20browser%20does%20not%20support%20audio%20recording"
      )
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
        Turbo.visit(
          "/notify?type=error&title=Upload%20failed&message=You're%20recording%20could%20not%20be%20uploaded"
        )
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
