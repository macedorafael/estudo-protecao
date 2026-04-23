/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        energisa: {
          DEFAULT: '#0077C8',
          dark: '#005A9E',
          light: '#E3F2FD',
        },
      },
    },
  },
  plugins: [],
}
