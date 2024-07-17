const config = {
  root: true,
  parserOptions: {
    ecmaVersion: 2022,
  },
  extends: [
    'eslint:recommended',
    'plugin:prettier/recommended',
  ],
  plugins: ['json'],
  ignorePatterns: ['node_modules', '.eslintrc.js'],
  rules: {
    'eol-last': ['error', 'always'],
  },
}

module.exports = {
  ...config,
}
