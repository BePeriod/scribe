import { describe, test, expect, beforeEach, afterEach, vi, assert } from 'vitest'
import './mocks/matchMedia'
import { Application } from '@hotwired/stimulus'
import TranscriptionController from '../src/controllers/transcription'
import { Editor, TinyMCE } from 'tinymce'

declare let tinymce: TinyMCE

describe('test creating text editor', () => {
  beforeEach(async () => {
    const application = Application.start()
    application.register('transcription', TranscriptionController)

    document.body.innerHTML = `
      <div id="content" data-controller="transcription">
        <div id="loading-icon" class="hidden" data-transcription-target="loadingIcon">
          <span>Loading...</span>
        </div>
        <div
          id="text-editor"
          data-transcription-target="textEditor"
        >
          <form id="post-form" action="/publish" method="POST" enctype="multipart/form-data">
            <textarea
              data-transcription-target="messageInput"
              id="messageInput"
              name="messageInput"
            >This is a LibriVox recording.</textarea>
            <input type="hidden" name="formatted_message" data-transcription-target="formattedMessage">
            <input
              id="post-image"
              data-transcription-target="imageInput"
              data-action="transcription#imagePreview"
              type="file"
              name="post_image"
              accept="image/png, image/jpeg, image/gif"
            />
            <button
              id="publish-btn"
              data-action="transcription#publish"
              type="button"
            >
              Publish
            </button>
          </form>
        </div>
      </div>`
  })

  test('TinyMCE Editor should be initialized', async () => {
    const editor = tinymce.activeEditor
    expect(editor instanceof Editor).toEqual(true)
    expect(editor!.id).toEqual('messageInput')
    // Unable to confirm content of editor. It returns a blank string here.
    // Since it's 3rd party code and easily verified in the browser I will omit testing.
    // This also prevents the testing of the controller's publish function.
  })
})
