const config = {
  root: true,
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 2022,
  },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:@typescript-eslint/recommended-requiring-type-checking',
    'plugin:prettier/recommended',
    'plugin:playwright/recommended',
  ],
  plugins: ['@typescript-eslint'],
  ignorePatterns: ['node_modules', '.eslintrc.js'],
  overrides: [
    {
      files: ['*.ts'],
      parserOptions: {
        project: ['./tsconfig.json'],
        tsconfigRootDir: __dirname,
      },
    },
  ],
  rules: {
    'no-console': 'off',
    'prefer-template': 'error',
    'eol-last': ['error', 'always'],
  },
}

module.exports = {
  ...config,
}
