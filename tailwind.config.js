/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        "playful-blue": "#80bfff",
        "vibrant-green": "#5FD38B",
        "sophisticated-gold": "#D4AF37",
        "soft-pink": "#F299B0",
        "neutral-gray": "#808080",
        "crisp-white": "#FFFFFF",
      },
      fontFamily: {
        inter: ["Inter", "sans-serif"],
        rubik: ["Rubik", "sans-serif"],
        roboto: ["Roboto", "sans-serif"],
      },
      height: {
        100: "26rem",
      },
      zIndex: {
        999: 999,
      },
    },
  },
  plugins: [],
};
