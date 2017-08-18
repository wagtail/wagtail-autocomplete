import React from 'react';
import { shallow } from 'enzyme';

import Single from './Single';


const mockProps = {
  suggestions: [
    { id: 1, title: 'Alice' },
    { id: 2, title: 'Tekisha' },
  ],
  selected: null,
  onChange: jest.fn(),
  onCreate: jest.fn(),
  onClick: jest.fn(),
  input: { value: '' },
  canCreate: true,
};


describe('Single', () => {
  it('exists', () => {
    expect(Single).toBeDefined();
  });

  it('mounts', () => {
    const single = shallow(
      <Single {...mockProps} />
    );
    expect(single).toMatchSnapshot();
  });
});
