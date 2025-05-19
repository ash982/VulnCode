// Example of a cross-database resolver
const Book = require('../models/book');
const driver = require('../config/neo4j-config');

const crossDbResolvers = {
  // Add a field to Neo4j's Person type that fetches related MySQL data
  Person: {
    authoredBooks: async (parent) => {
      // Use the person's name to find books in MySQL
      return await Book.findAll({
        where: {
          author: parent.name
        }
      });
    }
  },
  
  // Add a field to MySQL's Author type that fetches related Neo4j data
  Author: {
    actedInMovies: async (parent, _, context) => {
      const session = context.neo4jDriver.session();
      try {
        const result = await session.run(
          'MATCH (p:Person)-[:ACTED_IN]->(m:Movie) WHERE p.name = $name RETURN m',
          { name: parent.name }
        );
        return result.records.map(record => record.get('m').properties);
      } finally {
        await session.close();
      }
    }
  }
};

module.exports = crossDbResolvers;
