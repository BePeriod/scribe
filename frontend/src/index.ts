// import the css file so rollup is aware of it
import './global.css'

import * as Turbo from '@hotwired/turbo' /* eslint-disable-line @typescript-eslint/no-unused-vars -- loading for side effect */ /* eslint-disable-line no-unused-vars -- loading for side effect */
import { Application } from '@hotwired/stimulus'
import RecorderController from './controllers/recorder'
import RecordingController from './controllers/recording'

// update the global window type. This is needed for the window.stimulus line below.
// otherwise, the transpiler complains
declare global {
  interface Window {
    Stimulus: Application
  }
}

window.Stimulus = Application.start()
const Stimulus = window.Stimulus

Stimulus.register('recorder', RecorderController)
Stimulus.register('recording', RecordingController)
