// import the css file so rollup is aware of it
import './global.css'
// Import stimulus Application object
import { Application } from '@hotwired/stimulus'

// update the global window type. This is needed for the window.stimulus line below.
// otherwise, the transpiler complains
declare global {
    interface Window {
        Stimulus: Application
    }
}

window.Stimulus = Application.start()
const Stimulus = window.Stimulus

// is this thing on?
const message: string = "Hello, world!"
console.log(message)