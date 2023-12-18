/** @type {import('tailwindcss').Config} */
export default {
    content: [
        './templates/**/*.{html,j2}',
        './frontend/src/**/*.{js,ts}'
    ],
  theme: {
    extend: {},
  },
  plugins: [
      require('@tailwindcss/forms'),
  ],
}
