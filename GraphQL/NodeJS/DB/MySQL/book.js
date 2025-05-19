const { DataTypes } = require('sequelize');
const sequelize = require('../config/mysql-config');

const Book = sequelize.define('Book', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  title: {
    type: DataTypes.STRING,
    allowNull: false
  },
  author: {
    type: DataTypes.STRING,
    allowNull: false
  },
  publishedYear: {
    type: DataTypes.INTEGER
  }
});

module.exports = Book;
