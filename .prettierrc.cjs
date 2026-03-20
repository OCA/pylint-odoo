/** @type {import("prettier").Config} */
const config = {
  // https://github.com/prettier/prettier/issues/15388#issuecomment-1717746872
  plugins: [
    require.resolve("@prettier/plugin-xml"),
    require.resolve("prettier-plugin-toml"),
  ],
  bracketSpacing: false,
  printWidth: 119,
  proseWrap: "always",
  semi: true,
  trailingComma: "es5",
  xmlWhitespaceSensitivity: "strict",
};
module.exports = config;
