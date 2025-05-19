# The neo4j-graphql-js library handles parameterization internally when using @cypher directives, making it safer:

const { gql } = require('apollo-server');

const typeDefs = gql`
  type Person {
    id: ID!
    name: String!
  }

  type Query {
    # This is safe as neo4j-graphql-js handles parameterization internally
    personByName(name: String!): [Person] @cypher(
      statement: "MATCH (p:Person) WHERE p.name = $name RETURN p"
    )
  }
`;

module.exports = typeDefs;
