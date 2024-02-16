// import the css file so rollup is aware of it
import './global.css'

import * as Turbo from '@hotwired/turbo' /* eslint-disable-line @typescript-eslint/no-unused-vars -- loading for side effect */ /* eslint-disable-line no-unused-vars -- loading for side effect */
import { Application } from '@hotwired/stimulus'
import RecorderController from './controllers/recorder'
import RecordingController from './controllers/recording'
import TranscriptionController from './controllers/transcription'
import NotificationController from './controllers/notification'
import { LanguageToggleController } from './controllers/language-toggle'
import ComboboxController from './controllers/combobox'
import PublishOptionsController from './controllers/publish-options'

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
Stimulus.register('transcription', TranscriptionController)
Stimulus.register('notification', NotificationController)
Stimulus.register('language-toggle', LanguageToggleController)
Stimulus.register('combobox', ComboboxController)
Stimulus.register('publish-options', PublishOptionsController)
