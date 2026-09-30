/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        space: {
          950: '#111111', // Primary near-black surface
          900: '#161616', // Secondary technical surface
          850: '#1A1A1A', // Elevated workstation panel
          800: '#222222', // Interactive hover surface
          700: '#2C2C2C', // Hairline divider level
          600: '#383838', // Structural border
        },
        lunar: {
          100: '#F7F7F5', // Primary off-white typography
          200: '#E4E4E2', // High-contrast secondary
          300: '#C0C0BD', // Neutral reading text
          400: '#8C8C89', // Muted technical text
          500: '#646462', // De-emphasized labels
          600: '#3E3E3C', // Deep divider grey
        },
        editorial: {
          surface: '#F7F7F5',
          text: '#111111',
          subtle: '#E8E8E5',
          border: '#D4D4D0',
        },
        cyan: {
          accent: '#E4E4E2', // Remapped to neutral crisp off-white (no neon)
          glow: 'transparent',
        },
        azure: {
          accent: '#D0D0CE',
        },
        match: {
          green: '#4E9A51',  // Muted Sage ACCEPT state
          outlier: '#C64343', // Muted Rust REJECT state
          amber: '#C08420',   // Muted Ochre WARNING state
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        display: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['IBM Plex Mono', 'JetBrains Mono', 'Menlo', 'Consolas', 'monospace'],
      },
      animation: {
        'pulse-subtle': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'scan': 'scan 3s ease-in-out infinite',
        'reticle-spin': 'spin 12s linear infinite',
      },
      keyframes: {
        scan: {
          '0%, 100%': { transform: 'translateY(0%)', opacity: '0.2' },
          '50%': { transform: 'translateY(100%)', opacity: '0.8' },
        }
      }
    },
  },
  plugins: [],
}
