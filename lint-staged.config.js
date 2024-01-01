// lint-staged.config.js
export default {
  // Type check TypeScript files
  'frontend/src/**/*.(ts|tsx)': () => 'pnpm tsc --noEmit',

  // Lint then format TypeScript and JavaScript files
  'frontend/src/**/*.(ts|tsx|js)': (filenames) => [
    `pnpm eslint --fix ${filenames.join(' ')}`,
    `pnpm prettier --write ${filenames.join(' ')}`,
  ],

  // Format MarkDown and JSON
  '**/*.(md|json|css)': (filenames) => `pnpm prettier --write ${filenames.join(' ')}`,
}
