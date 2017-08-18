/* eslint no-underscore-dangle: 0 */
/**
 * WARNING:
 * This is NOT suitable for isomorphic applications.
 */
window._wagtailautocompleteUniqueId = 0;


const getUniqueId = () => `wagtailautocomplete-${window._wagtailautocompleteUniqueId++}`;


export default getUniqueId;
