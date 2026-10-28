/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        dark: {
          900: "#0b0f17",
          850: "#101622",
          800: "#161e2e",
          700: "#222d42",
          600: "#323f58",
        },
        accent: {
          blue: "#38bdf8",
          emerald: "#34d399",
          amber: "#fbbf24",
          rose: "#fb7185",
          purple: "#c084fc",
        }
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      }
    },
  },
  plugins: [],
}
