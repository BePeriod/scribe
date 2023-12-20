// import the css file so rollup is aware of it
import './global.css'
// Import stimulus Application object
import { Application } from '@hotwired/stimulus'
import RecorderController from './controllers/recorder'

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
