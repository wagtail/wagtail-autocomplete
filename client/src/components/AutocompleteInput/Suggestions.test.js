import React from 'react';
import { shallow } from 'enzyme';

import Suggestions from './Suggestions';


const mockProps = {
  suggestions: [
    { id: 1, title: 'Alice' },
    { id: 2, title: 'Tekisha' },
  ],
  onChange: jest.fn(),
  onCreate: jest.fn(),
  onClick: jest.fn(),
  input: { value: '' },
  canCreate: true,
};


describe('Suggestions', () => {
  it('exists', () => {
    expect(Suggestions).toBeDefined();
  });

  it('mounts', () => {
    const suggestions = shallow(
      <Suggestions {...mockProps} />
    );
    expect(suggestions).toMatchSnapshot();
  });

  it('does not show create new if input value is blank', () => {
    const suggestions = shallow(
      <Suggestions
        {...mockProps}
        input={{ value: ' ' }}
        canCreate={true}
      />
    );

    const item = suggestions.findWhere(node => (
      node.type() === 'li' &&
      node.text().startsWith('Create new')
    ));
    expect(item.exists()).toEqual(false);
  });

  it('does show create new if input value is not blank', () => {
    const suggestions = shallow(
      <Suggestions
        {...mockProps}
        input={{ value: 'new item' }}
        canCreate={true}
      />
    );

    const item = suggestions.findWhere(node => (
      node.type() === 'li' &&
      node.text().startsWith('Create new') &&
      node.text().includes('new item')
    ));
    expect(item.exists()).toEqual(true);
  });
});
