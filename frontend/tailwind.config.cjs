// tailwind.config.cjs
module.exports = {
  darkMode: "class", // ← important: use 'class' so toggling 'dark' on <html> works
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}"
  ],
  theme: { extend: {} },
  plugins: [],
};
