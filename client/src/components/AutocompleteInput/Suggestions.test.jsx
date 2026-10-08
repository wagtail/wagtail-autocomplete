import { fireEvent, render, screen } from '@testing-library/react';
import React from 'react';

import Suggestions from './Suggestions';


const mockProps = {
  suggestions: [
    { pk: 1, title: 'Alice' },
    { pk: 2, title: 'Tekisha' },
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

  it('renders a combobox input', () => {
    render(<Suggestions {...mockProps} />);
    expect(screen.getByRole('combobox')).toBeInTheDocument();
  });

  it('does not show create new if input value is blank', () => {
    render(
      <Suggestions
        {...mockProps}
        input={{ value: ' ' }}
        canCreate={true}
      />
    );

    expect(screen.queryByText(/Create new/)).not.toBeInTheDocument();
  });

  it('does show create new if input value is not blank', () => {
    render(
      <Suggestions
        {...mockProps}
        input={{ value: 'new item' }}
        canCreate={true}
      />
    );

    expect(screen.getByText(/Create new.*new item/)).toBeInTheDocument();
  });

  it('sets the correct aria owns id', () => {
    render(<Suggestions {...mockProps} />);

    const input = screen.getByRole('combobox');
    const list = screen.getByRole('listbox', { hidden: true });
    expect(list.id).toBeTruthy();
    expect(input.getAttribute('aria-owns')).toEqual(list.id);
  });

  it('sets the correct aria active descendant id on focus', () => {
    render(<Suggestions {...mockProps} />);

    const input = screen.getByRole('combobox');
    expect(input.getAttribute('aria-activedescendant')).toBeFalsy();

    fireEvent.focus(input);

    const options = screen.getAllByRole('option', { hidden: true });
    expect(input.getAttribute('aria-activedescendant')).toBeTruthy();
    expect(input.getAttribute('aria-activedescendant')).toEqual(options[0].id);
    expect(options[0].id === options[1].id).toEqual(false);
  });
});
