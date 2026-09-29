import { fireEvent, render, screen } from '@testing-library/react';
import React from 'react';

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
  it('exists', () => {
    expect(Multi).toBeDefined();
  });

  it('shows a message when nothing is selected', () => {
    render(<Multi {...mockProps} />);
    expect(screen.getByText('Nothing selected.')).toBeInTheDocument();
  });

  it('lists the selected items with a remove button each', () => {
    render(
      <Multi
        {...mockProps}
        selections={[{ pk: 1, title: 'Alice' }]}
      />
    );
    expect(screen.getByText('Alice')).toBeInTheDocument();
    expect(screen.queryByText('Nothing selected.')).not.toBeInTheDocument();
  });

  it('calls onClick with the remaining selections when removed', () => {
    const onClick = jest.fn();
    render(
      <Multi
        {...mockProps}
        selections={[{ pk: 1, title: 'Alice' }, { pk: 2, title: 'Tekisha' }]}
        onClick={onClick}
      />
    );
    fireEvent.click(screen.getAllByRole('button', { name: /remove/i })[0]);
    expect(onClick).toHaveBeenCalledWith([{ pk: 2, title: 'Tekisha' }]);
  });

  it('only suggests items that are not already selected', () => {
    render(
      <Multi
        {...mockProps}
        selections={[{ pk: 1, title: 'Alice' }]}
      />
    );
    expect(screen.queryByText('Alice')).not.toBeNull();
    expect(screen.getAllByText('Alice')).toHaveLength(1);
    expect(screen.getByText('Tekisha')).toBeInTheDocument();
  });
});
