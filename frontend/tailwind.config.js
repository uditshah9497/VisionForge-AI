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
        forge: {
          950: '#030712',
          900: '#0B0F19',
          850: '#111827',
          800: '#1E293B',
          700: '#334155',
          cyan: '#06B6D4',
          electric: '#3B82F6',
          neon: '#00F0FF',
          amber: '#F59E0B',
          emerald: '#10B981',
          rose: '#EF4444'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      }
    },
  },
  plugins: [],
}
