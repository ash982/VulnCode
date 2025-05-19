const { DataTypes } = require('sequelize');
const sequelize = require('../config/mysql-config');

const Author = sequelize.define('Author', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  name: {
    type: DataTypes.STRING,
    allowNull: false
  },
  birthYear: {
    type: DataTypes.INTEGER
  }
});

module.exports = Author;
