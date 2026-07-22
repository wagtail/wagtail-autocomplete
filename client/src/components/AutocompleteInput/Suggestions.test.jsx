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

  it('sets the correct aria owns id', () => {
    const suggestions = shallow(
      <Suggestions {...mockProps} />
    );

    const ariaOwnsId = suggestions.find('input').prop('aria-owns');
    const id = suggestions.find('ul').prop('id');
    expect(id).toBeTruthy();
    expect(id).toEqual(ariaOwnsId);
  });

  it('sets the correct aria active descendant id', () => {
    const suggestions = shallow(
      <Suggestions {...mockProps} />
    );

    let activeDescendantId = suggestions.find('input').prop('aria-activedescendant');
    expect(activeDescendantId).toBeFalsy();

    suggestions.setState({ visible: true, index: 0 });
    activeDescendantId = suggestions.find('input').prop('aria-activedescendant');
    const selectedOptionId = suggestions.find('li').get(0).props.id;
    const differentOptionId = suggestions.find('li').get(1).props.id;
    expect(activeDescendantId).toBeTruthy();
    expect(differentOptionId).toBeTruthy();
    expect(activeDescendantId).toEqual(selectedOptionId);
    expect(selectedOptionId === differentOptionId).toEqual(false);
  });
});
