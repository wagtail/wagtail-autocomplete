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
    rules: {
      // Spreading a mockProps fixture into JSX is the standard way to build
      // test cases; the rule's concern about unknown/unauditable props on
      // rendered output doesn't apply to test fixtures.
      'react/jsx-props-no-spreading': 'off',
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
