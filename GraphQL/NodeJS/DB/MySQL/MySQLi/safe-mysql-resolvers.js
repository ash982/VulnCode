const { Book, Author } = require('../models/associations');

const mysqlResolvers = {
  Query: {
    // Safe: Sequelize handles parameterization internally
    author: async (_, { id }) => {
      return await Author.findByPk(id);
    },
    
    // Safe: Sequelize handles WHERE clause parameterization
    booksByAuthor: async (_, { authorName }) => {
      return await Book.findAll({
        include: [{
          model: Author,
          where: { 
            name: authorName  // This is automatically parameterized
          }
        }]
      });
    }
  }
};

module.exports = mysqlResolvers;
