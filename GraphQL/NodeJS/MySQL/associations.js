const Book = require('./book');
const Author = require('./author');

// Define the relationship between models
Book.belongsTo(Author);
Author.hasMany(Book);

module.exports = { Book, Author };
