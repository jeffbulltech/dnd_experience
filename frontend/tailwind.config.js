/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        parchment: "#f3e9dc",
        "arcane-blue": "#1e3a8a",
        "ember-red": "#b91c1c",
        "forest-green": "#065f46"
      },
      fontFamily: {
        serif: ["'IM Fell English SC'", "serif"],
        sans: ["'Inter'", "sans-serif"]
      }
    }
  },
  plugins: []
};
