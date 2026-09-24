/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#eef1f6",
        ink: "#162033",
        muted: "#6b7a90",
        line: "#dde3ec",
        navy: "#1a2e4a",
        accent: "#2f5f9e",
        "accent-soft": "#e8f0fa",
        badge: "#0d8f7f",
        "badge-bg": "#e6f7f4",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      boxShadow: {
        panel: "0 1px 2px rgba(16, 32, 64, 0.04), 0 8px 24px rgba(16, 32, 64, 0.06)",
        input: "0 1px 2px rgba(16, 32, 64, 0.05), 0 12px 32px rgba(16, 32, 64, 0.08)",
      },
    },
  },
  plugins: [],
};
