/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'glas-green': '#22c55e',
        'glas-red': '#ef4444',
      }
    },
  },
  plugins: [],
}
