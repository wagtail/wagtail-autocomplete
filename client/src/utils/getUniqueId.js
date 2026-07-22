/* eslint no-underscore-dangle: 0 */
/**
 * WARNING:
 * This is NOT suitable for isomorphic applications.
 */
window._wagtailautocompleteUniqueId = 0;

const getUniqueId = () => {
	const id = window._wagtailautocompleteUniqueId;
	window._wagtailautocompleteUniqueId += 1;
	return `wagtailautocomplete-${id}`;
};

export default getUniqueId;
