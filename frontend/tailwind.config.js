/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{vue,js}"],
  theme: {
    extend: {
      fontFamily: {
        khmer: ["'Kantumruy Pro'", "'Noto Sans Khmer'", "sans-serif"],
      },
      colors: {
        brand: {
          50: "#eef7ff",
          100: "#d9edff",
          200: "#bce0ff",
          300: "#8ecdff",
          400: "#59b1ff",
          500: "#3390ff",
          600: "#1c6ff2",
          700: "#1758d6",
          800: "#1a48ac",
          900: "#1b3f88",
        },
        accent: {
          400: "#f6a94a",
          500: "#f2872a",
          600: "#e06d16",
        },
      },
      boxShadow: {
        soft: "0 10px 30px -12px rgba(23, 88, 214, 0.25)",
        card: "0 4px 20px rgba(15, 23, 42, 0.06)",
      },
      borderRadius: {
        xl2: "1.25rem",
      },
    },
  },
  plugins: [],
};
