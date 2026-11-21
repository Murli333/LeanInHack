/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: ['class', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        bg: 'var(--bg)',
        surface: 'var(--surface)',
        'surface-2': 'var(--surface-2)',
        border: 'var(--border)',
        primary: 'var(--primary)',
        'on-primary': 'var(--on-primary)',
        accent: 'var(--accent)',
        text: 'var(--text)',
        'text-muted': 'var(--text-muted)',
        danger: 'var(--danger)',
        'danger-tint': 'var(--danger-tint)',
        warn: 'var(--warn)',
        'warn-tint': 'var(--warn-tint)',
        safe: 'var(--safe)',
        'safe-tint': 'var(--safe-tint)',
        unknown: 'var(--unknown)',
        'unknown-tint': 'var(--unknown-tint)',
      },
      boxShadow: {
        'glow-danger': 'var(--glow-danger)',
        'card-soft': '0 4px 20px -2px rgba(0, 0, 0, 0.05), 0 2px 6px -1px rgba(0, 0, 0, 0.03)',
      },
      borderRadius: {
        'card': '18px',
        'card-lg': '22px',
        'pill': '9999px',
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
