import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';

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
  it('renders a combobox with the given suggestions once focused', () => {
    render(<Suggestions {...mockProps} />);

    const input = screen.getByRole('combobox');
    fireEvent.focus(input);

    expect(screen.getByRole('option', { name: 'Alice' })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: 'Tekisha' })).toBeInTheDocument();
  });

  it('does not show create new if input value is blank', () => {
    render(
      <Suggestions
        {...mockProps}
        input={{ value: ' ' }}
        canCreate={true}
      />
    );

    fireEvent.focus(screen.getByRole('combobox'));

    // The "create new" item doesn't carry role="option" like the other
    // suggestions do, so it can't be queried by role like they can.
    expect(
      screen.queryByText((content, element) => (
        element.tagName === 'LI' && element.textContent.startsWith('Create new')
      ))
    ).not.toBeInTheDocument();
  });

  it('does show create new if input value is not blank', () => {
    render(
      <Suggestions
        {...mockProps}
        input={{ value: 'new item' }}
        canCreate={true}
      />
    );

    fireEvent.focus(screen.getByRole('combobox'));

    expect(
      screen.getByText((content, element) => (
        element.tagName === 'LI' &&
        element.textContent.startsWith('Create new') &&
        element.textContent.includes('new item')
      ))
    ).toBeInTheDocument();
  });

  it('sets the correct aria owns id', () => {
    render(<Suggestions {...mockProps} />);

    const input = screen.getByRole('combobox');
    fireEvent.focus(input);

    const listbox = screen.getByRole('listbox');
    expect(listbox.id).toBeTruthy();
    expect(input).toHaveAttribute('aria-owns', listbox.id);
  });

  it('sets the correct aria active descendant id', () => {
    render(<Suggestions {...mockProps} />);

    const input = screen.getByRole('combobox');
    expect(input.getAttribute('aria-activedescendant')).toBeFalsy();

    fireEvent.focus(input);

    const options = screen.getAllByRole('option');
    expect(options[0].id).toBeTruthy();
    expect(options[1].id).toBeTruthy();
    expect(input).toHaveAttribute('aria-activedescendant', options[0].id);
    expect(options[0].id === options[1].id).toEqual(false);
  });
});
