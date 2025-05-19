const { gql } = require('apollo-server');
const neo4jTypeDefs = require('./neo4j-schema');
const mysqlTypeDefs = require('./mysql-schema');

// Create a "merge" type definition for the server
const rootTypeDefs = gql`
  type Query {
    _empty: String
  }

  type Mutation {
    _empty: String
  }
`;

module.exports = [rootTypeDefs, neo4jTypeDefs, mysqlTypeDefs];


const neo4jResolvers = require('./neo4j-resolvers');
const mysqlResolvers = require('./mysql-resolvers');

// Merge the resolvers
const resolvers = {
  Query: {
    ...neo4jResolvers.Query,
    ...mysqlResolvers.Query
  },
  Mutation: {
    ...neo4jResolvers.Mutation,
    ...mysqlResolvers.Mutation
  },
  // Include entity resolvers
  Author: mysqlResolvers.Author,
  Book: mysqlResolvers.Book,
  // Add neo4j entity resolvers if any
  Person: neo4jResolvers.Person,
  Movie: neo4jResolvers.Movie
};

module.exports = resolvers;
