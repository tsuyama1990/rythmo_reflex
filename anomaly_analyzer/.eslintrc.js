module.exports = {
  plugins: ["jsx-a11y", "tailwindcss"],
  extends: [
    "plugin:jsx-a11y/strict",
    "plugin:tailwindcss/recommended"
  ],
  rules: {
    "jsx-a11y/click-events-have-key-events": "error",
    "jsx-a11y/no-static-element-interactions": "error",
    "tailwindcss/no-custom-classname": "error",
    "tailwindcss/no-arbitrary-value": "warn"
  }
};
