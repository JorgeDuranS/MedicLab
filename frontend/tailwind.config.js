/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Mint color palette - Primary brand color
        'mint': {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#A8D8C9', // Primary mint color from design
          600: '#8BC5B8',
          700: '#6EB2A7',
          800: '#519F96',
          900: '#348C85',
        },
        // Professional dark blue palette
        'professional': {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#2D4A53', // Professional dark blue from design
          900: '#1e3338',
        },
        // Semantic colors
        'background': '#F7F9F8', // Light background from design
        'card': '#FFFFFF', // Pure white for cards
        'alert': '#E57373', // Soft red for alerts and cancellations
        // Role-specific accent colors
        'patient': '#A8D8C9',
        'doctor': '#B8E6D3', // Lighter mint variant for doctor theme
        'admin': '#4A6741', // Darker green for admin functions
      },
      fontFamily: {
        'heading': ['Poppins', 'Lato', 'sans-serif'],
        'body': ['Nunito Sans', 'Inter', 'sans-serif'],
      },
      fontSize: {
        'h1': ['2rem', { lineHeight: '2.5rem', fontWeight: '600' }],
        'h2': ['1.5rem', { lineHeight: '2rem', fontWeight: '600' }],
        'h3': ['1.25rem', { lineHeight: '1.75rem', fontWeight: '500' }],
        'body': ['1rem', { lineHeight: '1.5rem', fontWeight: '400' }],
        'small': ['0.875rem', { lineHeight: '1.25rem', fontWeight: '400' }],
      },
      boxShadow: {
        'card': '0 2px 8px rgba(0,0,0,0.1)',
        'card-hover': '0 4px 12px rgba(0,0,0,0.15)',
        'modal': '0 20px 40px rgba(0,0,0,0.2)',
      },
      borderRadius: {
        'card': '8px',
        'modal': '12px',
        'calendar': '12px',
      },
    },
  },
  plugins: [],
}