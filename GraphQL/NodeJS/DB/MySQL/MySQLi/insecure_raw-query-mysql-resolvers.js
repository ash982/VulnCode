const sequelize = require('../config/mysql-config');
const { QueryTypes } = require('sequelize');

const mysqlResolvers = {
  Query: {
    // If you need a raw query, use parameterization
    customBookSearch: async (_, { keyword }) => {
      // SAFE - uses parameterized query
      const books = await sequelize.query(
        'SELECT * FROM Books WHERE title LIKE :search',
        {
          replacements: { search: `%${keyword}%` },
          type: QueryTypes.SELECT
        }
      );
      return books;
    }
  }
};

module.exports = mysqlResolvers;
