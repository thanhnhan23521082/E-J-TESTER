import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        etest: {
          // Primary brand colors
          red: '#bb0016',
          'red-secondary': '#e42027',
          'red-light': '#fef2f2',
          // Backgrounds
          bg: '#f9f9ff',
          'bg-secondary': '#f0f3ff',
          'bg-login': '#f5f5f5',
          // Text colors
          text: '#151c27',
          subtext: '#5d3f3c',
          'nav-text': '#475569',
          muted: '#64748b',
          hint: '#94a3b8',
          // Status colors
          teal: '#0D9488',
          'teal-dark': '#0F6E56',
          'teal-light': '#CCFBF1',
          'teal-border': '#99F6E4',
          amber: '#F59E0B',
          'amber-bg': '#FEF3C7',
          green: '#10B981',
          'green-bg': '#D1FAE5',
          // Borders and shadows
          border: '#e7bdb8',
          'border-light': '#e7bdb803',
          shadow: '#0000000d',
          'shadow-secondary': '#e2e8f080',
        },
      },
      fontFamily: {
        sans: ['Be Vietnam Pro', 'Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        card: '12px',
        'form': '24px',
        pill: '9999px',
      },
      boxShadow: {
        'glass': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'card': '0 8px 8px -6px rgba(226, 232, 240, 0.5), 0 20px 22px -5px rgba(226, 232, 240, 0.5)',
        'button': '0 4px 4px -4px rgba(187, 0, 22, 0.2), 0 10px 13px -3px rgba(187, 0, 22, 0.2)',
      },
      backdropBlur: {
        'glass': '10.5px',
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '200% center' },
          '100%': { backgroundPosition: '-200% center' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-8px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(8px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        pulseGreen: {
          '0%, 100%': { boxShadow: '0 0 0 0 rgba(16,185,129,0.4)' },
          '70%': { boxShadow: '0 0 0 10px rgba(16,185,129,0)' },
        },
        bounce: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-25%)' },
        },
      },
      animation: {
        shimmer: 'shimmer 1.5s linear infinite',
        slideDown: 'slideDown 200ms ease-out',
        slideUp: 'slideUp 200ms ease-out',
        pulseGreen: 'pulseGreen 600ms ease-out',
      },
    },
  },
  plugins: [],
} satisfies Config
