/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'primary-blue': 'rgb(146, 179, 202)',
        'primary-orange': 'rgb(243, 195, 177)',
        'main-text': 'rgb(0, 43, 49)',
        'error-red': 'rgb(208, 69, 82)',
      },
      fontFamily: {
        sans: ['Open Sans', 'sans-serif'],
        urbanist: ['Urbanist', 'sans-serif'],
      }
    },
  },
  plugins: [],
}