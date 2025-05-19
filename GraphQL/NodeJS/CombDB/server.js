const { ApolloServer } = require('apollo-server');
const { makeAugmentedSchema } = require('neo4j-graphql-js');
const neo4jDriver = require('./config/neo4j-config');
const sequelize = require('./config/mysql-config');
const typeDefs = require('./schema');
const resolvers = require('./resolvers');

// Initialize MySQL models
require('./models/associations');

// Create Neo4j augmented schema
const neo4jSchema = makeAugmentedSchema({
  typeDefs: typeDefs[1], // neo4j-schema
  resolvers
});

// Create a new Apollo server
const server = new ApolloServer({
  typeDefs,
  resolvers,
  context: ({ req }) => ({
    neo4jDriver,
    // Include other context items as needed
  })
});

// Start the server after syncing the MySQL database
async function startServer() {
  try {
    // Sync MySQL models
    await sequelize.sync();
    console.log('MySQL database synchronized successfully');

    // Start the Apollo server
    const { url } = await server.listen();
    console.log(`🚀 Server ready at ${url}`);
  } catch (error) {
    console.error('Error starting server:', error);
  }
}

startServer();
