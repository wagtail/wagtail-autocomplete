import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import Multi from './Multi';


const mockProps = {
  suggestions: [
    { pk: 1, title: 'Alice' },
    { pk: 2, title: 'Tekisha' },
  ],
  selections: [],
  onChange: jest.fn(),
  onCreate: jest.fn(),
  onClick: jest.fn(),
  input: { value: '' },
  canCreate: true,
};


describe('Multi', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('shows a message when nothing is selected', () => {
    render(<Multi {...mockProps} />);
    expect(screen.getByText('Nothing selected.')).toBeInTheDocument();
  });

  it('lists each selection with a way to remove it', async () => {
    const user = userEvent.setup();
    const selections = [{ pk: 1, title: 'Alice' }];
    render(<Multi {...mockProps} selections={selections} />);

    expect(screen.getByText('Alice')).toBeInTheDocument();
    expect(screen.queryByText('Nothing selected.')).not.toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /remove/i }));
    expect(mockProps.onClick).toHaveBeenCalledWith([]);
  });

  it('excludes already-selected suggestions from the suggestion list', () => {
    render(<Multi {...mockProps} selections={[{ pk: 1, title: 'Alice' }]} />);
    fireEvent.focus(screen.getByRole('combobox'));

    expect(
      screen.queryByRole('option', { name: 'Alice' })
    ).not.toBeInTheDocument();
    expect(screen.getByRole('option', { name: 'Tekisha' })).toBeInTheDocument();
  });
});
