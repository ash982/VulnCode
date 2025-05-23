# Then use inputValidation.js in your resolvers:
const { validatePersonName } = require('../utils/inputValidation');
const driver = require('../config/neo4j-config');

const neo4jResolvers = {
  Query: {
    personByName: async (_, { name }) => {
      // Validate and sanitize input
      const validatedName = validatePersonName(name);
      
      const session = driver.session();
      try {
        const result = await session.run(
          'MATCH (p:Person) WHERE p.name = $name RETURN p',
          { name: validatedName }
        );
        return result.records.map(record => record.get('p').properties);
      } finally {
        await session.close();
      }
    }
  }
};

module.exports = neo4jResolvers;
