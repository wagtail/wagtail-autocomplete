import wagtailConfig from '@wagtail/eslint-config-wagtail';
import globals from 'globals';

export default [
  ...wagtailConfig,
  {
    files: ['**/*.js', '**/*.jsx'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        ...globals.browser,
      },
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
      },
    },
    settings: {
      react: {
        version: '16.14.0',
      },
      'import-x/extensions': ['.js', '.jsx'],
      'import-x/resolver': {
        node: {
          extensions: ['.js', '.jsx'],
        },
      },
    },
  },
  {
    files: ['**/*.test.js', '**/*.test.jsx'],
    languageOptions: {
      globals: {
        ...globals.jest,
      },
    },
  },
  {
    files: ['**/__mocks__/**'],
    languageOptions: {
      globals: {
        ...globals.commonjs,
      },
    },
  },
];
