const { gql } = require('apollo-server');

const typeDefs = gql`
  type Person {
    id: ID!
    name: String!
    born: Int
    acted_in: [Movie] @relation(name: "ACTED_IN", direction: "OUT")
    directed: [Movie] @relation(name: "DIRECTED", direction: "OUT")
  }

  type Movie {
    id: ID!
    title: String!
    released: Int
    tagline: String
    actors: [Person] @relation(name: "ACTED_IN", direction: "IN")
    directors: [Person] @relation(name: "DIRECTED", direction: "IN")
  }

  type Query {
    personByName(name: String!): [Person] @cypher(
      statement: "MATCH (p:Person) WHERE p.name CONTAINS $name RETURN p"
    )
    movieByTitle(title: String!): [Movie] @cypher(
      statement: "MATCH (m:Movie) WHERE m.title CONTAINS $title RETURN m"
    )
  }
`;

module.exports = typeDefs;
