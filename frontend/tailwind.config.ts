import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class", // ← required for ThemeContext to work
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./context/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      screens:{
        customs:"915px"
      }
    },
  },
  plugins: [],
};

export default config;