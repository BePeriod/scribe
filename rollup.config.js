import typescript from '@rollup/plugin-typescript'
import postcss from 'rollup-plugin-postcss'
import resolve from '@rollup/plugin-node-resolve'
import terser from '@rollup/plugin-terser'

export default {
  // use index.ts as the entrypoint
  input: 'frontend/src/index.ts',
  output: [
    {
      // configure output to go to the static folder
      file: 'static/dist/index.js',
      format: 'esm',
      sourcemap: true,
    },
  ],
  plugins: [
    // run PosCSS to generate Tailwind classes
    postcss({
      config: {
        path: './postcss.config.cjs',
      },
      extensions: ['.css'],
      minimize: true,
      // output the css file in /static/dist/global.css
      extract: 'global.css',
    }),
    resolve(),
    typescript({ tsconfig: './tsconfig.json' }),
    terser(),
  ],
}
