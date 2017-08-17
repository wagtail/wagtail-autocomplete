import React from 'react';
import { storiesOf } from '@storybook/react';
import { action } from '@storybook/addon-actions';

import Suggestions from '../components/AutocompleteInput/Suggestions'


const suggestions = [
  { id: 1, title: 'Alice' },
  { id: 2, title: 'Tekisha' },
]


storiesOf('Suggestions', module)
  .add('single input with suggestions', () => (
    <Suggestions
      suggestions={suggestions}
      onClick={action('on click')}
      onCreate={action('on create')}
      onChange={action('on change')}
      canCreate={true}
      isSingle={true}
      input=""
    />
  ));
