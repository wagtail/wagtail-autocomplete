import React from "react";
import { createRoot } from "react-dom/client";

import AutocompleteInput from "./AutocompleteInput";
import { nc } from "./nc";

const initAutocompleteInput = (autocompleteNode) => {
	const wagtailadminHome =
		autocompleteNode.dataset.autocompleteWagtailadminHome;
	const name = autocompleteNode.dataset.autocompleteInputName;
	const value = JSON.parse(autocompleteNode.dataset.autocompleteInputValue);
	const type = autocompleteNode.dataset.autocompleteInputType;
	const labelId = autocompleteNode.dataset.autocompleteInputId;
	const canCreate = autocompleteNode.dataset.autocompleteInputCanCreate === "";
	const isSingle = autocompleteNode.dataset.autocompleteInputIsSingle === "";

	const hasValidData = name && type;
	if (!hasValidData) {
		return;
	}

	const root = createRoot(autocompleteNode);
	root.render(
		<AutocompleteInput
			name={name}
			value={value}
			type={type}
			labelId={labelId}
			canCreate={canCreate}
			isSingle={isSingle}
			apiBase={wagtailadminHome + "autocomplete/"}
		/>,
	);
};

export default AutocompleteInput;

export { initAutocompleteInput, nc };
