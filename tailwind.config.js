/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'page-bg': '#020205',
        'card-bg': '#05050A',
        'elevated': '#080812',
        'neon-blue': {
          DEFAULT: '#00F0FF',
          glow: 'rgba(0, 240, 255, 0.4)',
          subtle: 'rgba(0, 240, 255, 0.1)',
        },
        'neon-purple': {
          DEFAULT: '#B026FF',
          glow: 'rgba(176, 38, 255, 0.4)',
        },
        'cyber-gray': '#8A9DB0'
      },
      fontFamily: {
        sans: ['"Rajdhani"', 'sans-serif'],
        display: ['"Orbitron"', 'sans-serif'],
        mono: ['"Michroma"', 'monospace'],
      }
    },
  },
  plugins: [],
}
