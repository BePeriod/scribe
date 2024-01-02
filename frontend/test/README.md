# Front End Testing

The unit tests for the front-end code are very sparse for now. This is due to a number of factors.

- The app is designed to minimize client side code, so most of the client side code required uses more
  specialized DOM features better tested by something like Playwright.

- The TinyMCE editor used also does not work well in a virtual dom environment and
  prevents some of the code from triggering as it would in the browser.
