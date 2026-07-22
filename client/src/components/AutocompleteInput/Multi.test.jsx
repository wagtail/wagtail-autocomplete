import React from 'react';
import { shallow } from 'enzyme';

import Multi from './Multi';


const mockProps = {
  suggestions: [
    { id: 1, title: 'Alice' },
    { id: 2, title: 'Tekisha' },
  ],
  selected: [],
  onChange: jest.fn(),
  onCreate: jest.fn(),
  onClick: jest.fn(),
  input: { value: '' },
  canCreate: true,
};


describe('Multi', () => {
  it('exists', () => {
    expect(Multi).toBeDefined();
  });

  it('mounts', () => {
    const multi = shallow(
      <Multi {...mockProps} />
    );
    expect(multi).toMatchSnapshot();
  });
});
