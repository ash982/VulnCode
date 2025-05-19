const { gql } = require('apollo-server');

const typeDefs = gql`
  type Author {
    id: ID!
    name: String!
    birthYear: Int
    books: [Book]
  }

  type Book {
    id: ID!
    title: String!
    publishedYear: Int
    author: Author
  }

  type Query {
    authors: [Author]
    author(id: ID!): Author
    books: [Book]
    book(id: ID!): Book
  }

  type Mutation {
    createAuthor(name: String!, birthYear: Int): Author
    createBook(title: String!, publishedYear: Int, authorId: ID!): Book
  }
`;

module.exports = typeDefs;
