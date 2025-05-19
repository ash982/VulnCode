# use parameterized queries instead of string concatenation.
const driver = require('../config/neo4j-config');

const neo4jResolvers = {
  Query: {
    personByName: async (_, { name }) => {
      const session = driver.session();
      try {
        // Safe - uses parameters
        const result = await session.run(
          'MATCH (p:Person) WHERE p.name = $name RETURN p',
          { name } // Parameters are passed as an object
        );
        return result.records.map(record => record.get('p').properties);
      } finally {
        await session.close();
      }
    }
  }
};

module.exports = neo4jResolvers;
