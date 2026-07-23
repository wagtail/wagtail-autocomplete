import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

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
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders suggestions when nothing is selected', () => {
    render(<Single {...mockProps} />);

    const input = screen.getByRole('combobox');
    expect(input).toBeInTheDocument();

    fireEvent.focus(input);
    expect(screen.getByRole('option', { name: 'Alice' })).toBeInTheDocument();
  });

  it('renders the selected item with a way to remove it', async () => {
    const user = userEvent.setup();
    render(<Single {...mockProps} selected={{ pk: 1, title: 'Alice' }} />);

    expect(screen.getByText('Alice')).toBeInTheDocument();
    expect(screen.queryByRole('combobox')).not.toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /remove/i }));
    expect(mockProps.onClick.mock.calls[0][0]).toBeNull();
  });
});
