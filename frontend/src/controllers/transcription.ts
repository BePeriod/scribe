import { Controller } from '@hotwired/stimulus'
import type { TinyMCE } from 'tinymce'

declare let tinymce: TinyMCE

export default class extends Controller {
  declare readonly messageInputTarget: HTMLInputElement
  declare readonly formattedMessageTarget: HTMLInputElement
  declare readonly imageInputTarget: HTMLInputElement
  declare readonly loadingIconTarget: HTMLElement
  static targets = ['messageInput', 'formattedMessage', 'imageInput', 'loadingIcon']

  async connect() {
    tinymce.activeEditor?.remove()
    const editorId = `#${this.messageInputTarget.id}`
    await tinymce.init({
      selector: editorId,
      menubar: false,
      toolbar: 'undo redo | bold italic | link image',
      statusbar: false,
    })
  }

  publish() {
    const content = tinymce.activeEditor?.getContent()
    if (content) {
      this.formattedMessageTarget.value = content
      this.formattedMessageTarget.form?.requestSubmit()
      this.loadingIconTarget.classList.remove('hidden')
    }
  }

  imagePreview() {
    if (this.imageInputTarget.files) {
      const [file] = this.imageInputTarget.files
      const url = URL.createObjectURL(file)
      const content = `${
        tinymce.activeEditor?.getContent() ?? ''
      }<p><img src="${url}" alt="image preview" width="100%" />`
      tinymce.activeEditor?.setContent(content)
    }
  }
}
