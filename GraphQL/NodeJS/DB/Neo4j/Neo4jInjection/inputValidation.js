const { UserInputError } = require('apollo-server');

function validatePersonName(name) {
  if (!name || typeof name !== 'string') {
    throw new UserInputError('Invalid name provided');
  }
  
  // Ensure name doesn't contain Cypher injection patterns
  const cypher_patterns = /[{}`\[\]()\\\/]/g;
  if (cypher_patterns.test(name)) {
    throw new UserInputError('Invalid characters in name');
  }
  
  return name.trim();
}

module.exports = { validatePersonName };
