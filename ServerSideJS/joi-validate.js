//Joi is a JavaScript library used for data validation. 
//It allows developers to define schemas for JavaScript objects and then validate data against those schemas. 
//It is commonly used in Node.js applications to ensure that data received from external sources, such as API requests, 
//conforms to the expected format and data types.

const Joi = require('@hapi/joi');

//Define a Schema
const schema = Joi.object({
  username: Joi.string().alphanum().min(3).max(30).required(),
  email: Joi.string().email().required(),
  password: Joi.string().min(8).required(),
});

//Use the validate method to validate your data against the schema:
const data = {
  username: 'johndoe',
  email: 'john.doe@example.com',
  password: 'password123',
};

const { error, value } = schema.validate(data);

if (error) {
  // Handle validation error
  console.error(error.details);
} else {
  // Data is valid
  console.log(value);
}
