import {
  AutocompleteInput,
  initAutocompleteInput
} from "./components/AutocompleteInput";

export { AutocompleteInput, initAutocompleteInput };

window.initAutoCompleteWidget = inputId => {
  const autocompleteInputNode = document.querySelector(
    `[data-autocomplete-input-id=${inputId}]`
  );
  initAutocompleteInput(autocompleteInputNode);
};
