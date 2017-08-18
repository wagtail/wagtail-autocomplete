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
  input: '',
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
});
