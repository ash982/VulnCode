// In-memory data store for demonstration
const books = [
  {
    id: '1',
    title: 'The Awakening',
    author: 'Kate Chopin',
    publishedYear: 1899
  },
  {
    id: '2',
    title: 'City of Glass',
    author: 'Paul Auster',
    publishedYear: 1985
  }
];

const resolvers = {
  Query: {
    books: () => books,
    book: (_, { id }) => books.find(book => book.id === id)
  },
  Mutation: {
    addBook: (_, { title, author, publishedYear }) => {
      const newBook = {
        id: String(books.length + 1),
        title,
        author,
        publishedYear
      };
      books.push(newBook);
      return newBook;
    }
  }
};

module.exports = resolvers;
