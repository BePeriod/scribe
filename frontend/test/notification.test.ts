import { describe, test, expect, beforeEach } from 'vitest'
import { Application } from '@hotwired/stimulus'
import NotificationController from '../src/controllers/notification'

describe('test closing notifications', () => {
  beforeEach(async () => {
    document.body.innerHTML = `<div data-controller="notification" id="notification-1">
        <p>I am a notification</p>
        <button id="close-btn" data-action="notification#disconnect">Close</button>
      </div>`

    const application = Application.start()
    application.register('notification', NotificationController)
  })

  test('notification should be visible', async () => {
    const div = document.getElementById('notification-1')
    expect(div?.classList.contains('opacity-100')).toEqual(true)
  })

  test('notification should be hidden', async () => {
    const div = document.getElementById('notification-1'),
      btn = document.getElementById('close-btn')
    expect(div?.classList.contains('opacity-100')).toEqual(true)
    btn?.click()
    expect(div?.classList.contains('opacity-100')).toEqual(false)
    expect(div?.classList.contains('opacity-0')).toEqual(true)
  })
})
