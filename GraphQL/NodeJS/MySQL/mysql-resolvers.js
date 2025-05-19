const { Book, Author } = require('../models/associations');

const mysqlResolvers = {
  Query: {
    authors: async () => await Author.findAll(),
    author: async (_, { id }) => await Author.findByPk(id),
    books: async () => await Book.findAll(),
    book: async (_, { id }) => await Book.findByPk(id)
  },
  Mutation: {
    createAuthor: async (_, { name, birthYear }) => {
      return await Author.create({ name, birthYear });
    },
    createBook: async (_, { title, publishedYear, authorId }) => {
      return await Book.create({ title, publishedYear, AuthorId: authorId });
    }
  },
  Author: {
    books: async (parent) => await Book.findAll({ where: { AuthorId: parent.id } })
  },
  Book: {
    author: async (parent) => await Author.findByPk(parent.AuthorId)
  }
};

module.exports = mysqlResolvers;
