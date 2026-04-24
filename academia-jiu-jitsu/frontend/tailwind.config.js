/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#fff1f2',
          100: '#ffe4e6',
          500: '#c41e3a',
          600: '#a31c31',
          700: '#881528',
          800: '#6e1021',
          900: '#580d1a',
        },
      },
    },
  },
  plugins: [],
}
