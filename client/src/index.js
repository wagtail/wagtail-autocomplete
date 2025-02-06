import AutocompleteInput, {
  initAutocompleteInput
} from "./components/AutocompleteInput";

export { AutocompleteInput, initAutocompleteInput };

window.initAutoCompleteWidget = autocompleteInputNode => {
  initAutocompleteInput(autocompleteInputNode);
};
