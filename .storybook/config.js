import { configure } from '@storybook/react';

function loadStories() {
  require('../client/src/stories/index.js');
}

configure(loadStories, module);
