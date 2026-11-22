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
        'surface-card': 'var(--surface-card)',
        border: 'var(--border)',
        'border-subtle': 'var(--border-subtle)',
        primary: 'var(--primary)',
        'primary-hover': 'var(--primary-hover)',
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
        'glow-blue': 'var(--glow-blue)',
        'card-soft': '0 4px 20px -2px rgba(0, 0, 0, 0.25), 0 2px 6px -1px rgba(0, 0, 0, 0.15)',
        'card-elevated': '0 10px 30px -5px rgba(0, 0, 0, 0.35), 0 4px 10px -2px rgba(0, 0, 0, 0.2)',
        'inner-highlight': 'inset 0 1px 1px 0 rgba(255, 255, 255, 0.08)',
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
