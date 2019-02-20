import {
  AutocompleteInput,
  initAutocompleteInput
} from "./components/AutocompleteInput";

export { AutocompleteInput, initAutocompleteInput };

window.initAutoComplete = () => {
  const autocompleteInputNodes = document.querySelectorAll(
    "[data-autocomplete-input]"
  );
  autocompleteInputNodes.forEach(initAutocompleteInput);
};
