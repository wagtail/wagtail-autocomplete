export const namespaceClassName = (base) => (className) => {
  if (!className) {
    return base;
  }

  const parts = Array.isArray(className) ? className : className.split(' ');
  return parts.map(name => `${base}__${name}`).join(' ');
};
