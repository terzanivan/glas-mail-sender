/** @type {import('tailwindcss').Config} */
export default {
	content: [
		"./index.html",
		"./src/**/*.{vue,js,ts,jsx,tsx}",
	],
	theme: {
		extend: {
			colors: {
				'glas-text-accent': '#9576cd',
				'glas-black': '#131313',
				'glas-green': '#22c55e',
				'glas-red': '#ef4444',
			}
		},
	},
	plugins: [],
}
