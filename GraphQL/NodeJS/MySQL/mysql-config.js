const { Sequelize } = require('sequelize');

const sequelize = new Sequelize(
  process.env.MYSQL_DATABASE || 'database',
  process.env.MYSQL_USER || 'user',
  process.env.MYSQL_PASSWORD || 'password',
  {
    host: process.env.MYSQL_HOST || 'localhost',
    dialect: 'mysql',
    pool: {
      max: 5,
      min: 0,
      acquire: 30000,
      idle: 10000
    },
    logging: false
  }
);

module.exports = sequelize;
