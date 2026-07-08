/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: '#0B1F3A',
          light: '#1E3A5F',
          dark: '#071527',
        },
        cream: '#F7F5F0',
        brass: {
          DEFAULT: '#C9A34E',
          light: '#DFC077',
          dark: '#A6803A',
        },
        alert: {
          DEFAULT: '#B23A3A',
          light: '#D9E9E4',
        },
        ink: '#1A1F2B',
      },
      fontFamily: {
        display: ['var(--font-fraunces)', 'serif'],
        body: ['var(--font-inter)', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
