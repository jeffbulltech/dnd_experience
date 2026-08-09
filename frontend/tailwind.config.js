/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // "vellum" — warm aged-leather parchment, deeper and smokier than the old beige paper
        parchment: {
          DEFAULT: "#e8d9b5",
          50: "#faf3e3",
          100: "#f0e2bd",
          200: "#e3cd94",
          300: "#cfab63",
          400: "#b3893f"
        },
        // "arcane-blue" retained as the identifier so all existing component
        // markup stays valid, re-hued from royal blue to a deep grimoire violet
        "arcane-blue": {
          DEFAULT: "#482575",
          50: "#f4f0fb",
          100: "#e6dbf5",
          200: "#cbb3ea",
          300: "#ab85d9",
          400: "#8c5cc4",
          500: "#6f3fac",
          600: "#5a2f8f",
          700: "#482575",
          800: "#3a1d5e",
          900: "#2a1444"
        },
        // wax-seal crimson
        "ember-red": {
          DEFAULT: "#741a17",
          50: "#fdecea",
          100: "#f9cfc9",
          200: "#f0a199",
          300: "#e2726a",
          400: "#cf4a42",
          500: "#b52f29",
          600: "#93221e",
          700: "#741a17",
          800: "#591310",
          900: "#3d0c0a"
        },
        // deep verdant emerald
        "forest-green": {
          DEFAULT: "#125234",
          50: "#eefaf1",
          100: "#cdf0d9",
          200: "#96deae",
          300: "#5cc386",
          400: "#34a366",
          500: "#1f8350",
          600: "#166840",
          700: "#125234",
          800: "#0e3f28",
          900: "#0a2e1e"
        },
        // aged brass / antique gold, warmer and duller than bright yellow-gold
        "dragon-gold": {
          DEFAULT: "#c88a2c",
          50: "#fdf6e3",
          100: "#f8e7b8",
          200: "#eeca79",
          300: "#e0aa45",
          400: "#c88a2c",
          500: "#a86c1f",
          600: "#8a5518",
          700: "#6c4113",
          800: "#4f2e0e",
          900: "#35200a"
        },
        "shadow-black": "#15100c",
        "ink-black": "#08070a",
        // low-flame torchlight amber, used for glows and highlights
        torchlight: {
          DEFAULT: "#e08a2e",
          200: "#f6cf94",
          400: "#e08a2e",
          600: "#b0621a"
        }
      },
      fontFamily: {
        serif: ["'EB Garamond'", "serif"],
        sans: ["'Inter'", "sans-serif"],
        display: ["'Cinzel Decorative'", "'Cinzel'", "serif"]
      },
      backgroundImage: {
        "parchment-texture": "url(\"data:image/svg+xml,%3Csvg width='100' height='100' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100' height='100' filter='url(%23noise)' opacity='0.05'/%3E%3C/svg%3E\")",
        "aged-paper": "linear-gradient(to bottom, rgba(232, 217, 181, 0.85), rgba(207, 171, 99, 0.92)), url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23000000' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")",
        "torch-glow": "radial-gradient(ellipse 900px 700px at 15% 0%, rgba(224, 138, 46, 0.16), transparent 60%), radial-gradient(ellipse 900px 700px at 85% 100%, rgba(72, 37, 117, 0.22), transparent 60%), linear-gradient(160deg, #0e0b08 0%, #15100c 45%, #1c1510 100%)"
      },
      boxShadow: {
        "parchment": "0 4px 6px -1px rgba(0, 0, 0, 0.25), 0 2px 4px -1px rgba(0, 0, 0, 0.15), inset 0 1px 0 0 rgba(255, 255, 255, 0.15)",
        "scroll": "0 10px 15px -3px rgba(0, 0, 0, 0.35), 0 4px 6px -2px rgba(0, 0,0, 0.2), inset 0 0 0 1px rgba(0, 0, 0, 0.08)",
        "ornate": "0 0 0 1px rgba(200, 138, 44, 0.25), 0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -1px rgba(0, 0, 0, 0.12)",
        "torch": "0 0 24px 4px rgba(224, 138, 46, 0.35)"
      },
      borderWidth: {
        "3": "3px"
      }
    }
  },
  plugins: []
};
