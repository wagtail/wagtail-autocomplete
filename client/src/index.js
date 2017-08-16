import {
  AutocompleteInput,
  initAutocompleteInput,
} from './components/AutocompleteInput';


export {
  AutocompleteInput,
  initAutocompleteInput,
};


document.addEventListener('DOMContentLoaded', () => {
  const autocompleteInputNodes = document.querySelectorAll('[data-autocomplete-input]');
  autocompleteInputNodes.forEach(initAutocompleteInput);
});
