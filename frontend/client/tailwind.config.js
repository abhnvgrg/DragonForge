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
        // NeuroLens Monochromatic Palette
        neurolens: {
          // Background
          bg: '#09090B',           // Matte Black
          // Surfaces
          surface: '#18181B',       // Dark Charcoal
          surfaceHover: '#1F1F23',  // Slightly lighter charcoal
          // Borders
          border: '#27272A',        // Thin subtle border
          borderHover: '#3F3F46',   // Hover border
          // Text
          textPrimary: '#FAFAFA',   // Crisp Pure White
          textSecondary: '#A1A1AA', // Muted Neutral Grey
          textMuted: '#71717A',     // More muted grey
          // Badge colors
          badgeEstablished: '#FFFFFF', // White background
          badgeEstablishedText: '#000000', // Black text
          badgeMeasured: '#3F3F46', // Mid-grey background
          badgeMeasuredText: '#FFFFFF', // White text
          badgeExploratory: 'transparent', // Transparent
          badgeExploratoryBorder: '#FAFAFA', // White dashed border
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'SF Mono', 'Monaco', 'monospace'],
      },
      fontSize: {
        'display': ['3.5rem', { lineHeight: '1.1', letterSpacing: '-0.02em', fontWeight: '700' }],
        'headline': ['1.5rem', { lineHeight: '1.3', letterSpacing: '-0.01em', fontWeight: '600' }],
        'title': ['1.125rem', { lineHeight: '1.4', fontWeight: '500' }],
        'body': ['1rem', { lineHeight: '1.6' }],
        'small': ['0.875rem', { lineHeight: '1.5' }],
        'tiny': ['0.75rem', { lineHeight: '1.5' }],
      },
      spacing: {
        'panel': '1.5rem',  // 24px - generous panel padding
        'panel-sm': '1rem', // 16px
        'panel-lg': '2rem', // 32px
      },
      borderRadius: {
        'panel': '0.5rem', // 8px
        'badge': '9999px', // Full pill
      },
      boxShadow: {
        'panel': '0 1px 3px 0 rgb(0 0 0 / 0.3), 0 1px 2px -1px rgb(0 0 0 / 0.2)',
        'panel-hover': '0 4px 6px -1px rgb(0 0 0 / 0.3), 0 2px 4px -2px rgb(0 0 0 / 0.2)',
      },
    },
  },
  plugins: [],
}