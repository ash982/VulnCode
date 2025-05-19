const driver = require('../config/neo4j-config');

const neo4jResolvers = {
  Query: {
    // These can be augmented or overridden if the @cypher directives aren't sufficient
    personByName: async (_, { name }) => {
      const session = driver.session();
      try {
        const result = await session.run(
          'MATCH (p:Person) WHERE p.name CONTAINS $name RETURN p',
          { name }
        );
        return result.records.map(record => record.get('p').properties);
      } finally {
        await session.close();
      }
    }
  }
};

module.exports = neo4jResolvers;
