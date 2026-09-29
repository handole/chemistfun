/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        chemist: {
          dark: '#121726',
          darker: '#0B0F19',
          navy: '#1A2138',
          card: '#FFFFFF',
          bg: '#F6F8FC',
          border: '#E2E8F0',
          primary: '#2563EB',
          accent: '#7C3AED',
          amber: '#F59E0B',
          emerald: '#10B981',
          sky: '#0284C7'
        }
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
        '4xl': '2rem',
      },
      boxShadow: {
        'soft': '0 4px 20px -2px rgba(0, 0, 0, 0.05)',
        'card': '0 2px 12px -2px rgba(26, 33, 56, 0.06)',
        'elevated': '0 10px 30px -4px rgba(26, 33, 56, 0.08)',
      }
    },
  },
  plugins: [],
}

