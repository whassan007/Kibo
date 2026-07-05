export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        bauhaus: {
          black: '#F5F2EB',      // Warm Sand background
          white: '#111111',      // Charcoal body text
          grey: '#FFFFFF',       // Card background
          mediumgrey: '#D1CDBF', // Muted Sand border
          lightgrey: '#706E64',  // Muted secondary text
          accent: '#B87B31',     // Ochre/amber accent
          red: '#C84630',        // Rust Red warning/drift
          yellow: '#D69E2E'      // Warm Amber warning
        }
      },
      fontFamily: {
        sans: ['Inter', 'Futura', 'Helvetica', 'Arial', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
