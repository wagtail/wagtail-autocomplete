import { fireEvent, render, screen } from '@testing-library/react';
import React from 'react';

import Single from './Single';


const mockProps = {
  suggestions: [
    { pk: 1, title: 'Alice' },
    { pk: 2, title: 'Tekisha' },
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

  it('renders the suggestions input when nothing is selected', () => {
    render(<Single {...mockProps} />);
    expect(screen.getByRole('combobox')).toBeInTheDocument();
  });

  it('renders the selected item and a remove button when something is selected', () => {
    render(<Single {...mockProps} selected={{ pk: 1, title: 'Alice' }} />);
    expect(screen.getByText('Alice')).toBeInTheDocument();
    expect(screen.queryByRole('combobox')).not.toBeInTheDocument();
  });

  it('calls onClick with null when the remove button is clicked', () => {
    const onClick = jest.fn();
    render(
      <Single
        {...mockProps}
        selected={{ pk: 1, title: 'Alice' }}
        onClick={onClick}
      />
    );
    fireEvent.click(screen.getByRole('button', { name: /remove/i }));
    expect(onClick).toHaveBeenCalledWith(null, expect.anything());
  });
});
