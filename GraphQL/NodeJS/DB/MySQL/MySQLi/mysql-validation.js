const { UserInputError } = require('apollo-server');

function validateId(id) {
  const parsed = parseInt(id, 10);
  
  if (isNaN(parsed) || parsed.toString() !== id.toString()) {
    throw new UserInputError('Invalid ID format');
  }
  
  return parsed;
}

function sanitizeSearchTerm(term) {
  if (!term || typeof term !== 'string') {
    throw new UserInputError('Invalid search term');
  }
  
  // Remove any potentially dangerous characters
  return term.replace(/[;'"\\]/g, '');
}

module.exports = { validateId, sanitizeSearchTerm };
