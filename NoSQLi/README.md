ServerSide JS injection: 
https://www.mongodb.com/docs/upcoming/core/server-side-javascript/
Server-side JavaScript Deprecated
Starting in MongoDB 8.0, server-side JavaScript functions ($accumulator, $function, $where) are deprecated. MongoDB logs a warning when you run these functions.
Map-reduce is deprecated starting in MongoDB 5.0.


## Summary: Safe vs. unsafe query filters

| Approach |	Code snippet |	Result |	Is it safe? | 
| :---- | :---- | :--- | :---- |
| Vulnerable (original example) |	query_filter = {'username': username, 'password': password}	| Attacker sends password={"$ne": null}. PyMongo interprets this as a nested document and executes the operator.	| No
| Incorrect (your proposed fix) |  query_filter = {username: username, password: password}	| Raises a NameError in Python because username is not defined as a variable for the dictionary key.	| No, but it breaks.
  | Secure (correct fix)	| username = str(request.form.get('username')) password = str(request.form.get('password'))  query_filter = {'username': username, 'password': password} | The str() cast prevents PyMongo from interpreting any user input as an operator. | Yes

**Vulnerable Example**
```python
from pymongo import MongoClient
from flask import Flask, request

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client.test_database

# Vulnerable route
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Insecure query using user input directly
    user = db.users.find_one({
        'username': username,
        'password': password
    })
    
    if user:
        return 'Login successful!'
    else:
        return 'Invalid credentials'
```


**Injection exploit: Authentication bypass**
An attacker can provide a specially crafted password that modifies the query's logic to make the password check always evaluate to true. 
Attacker's input:
username: admin
password: {"$ne": null} (or its URL-encoded equivalent) 
What happens behind the scenes:
The Python application receives the username and password values from the request.
The application constructs a query dictionary, but the JSON-like password value is treated as a nested document instead of a string.
The resulting MongoDB query becomes:
```json
{
  "username": "admin",
  "password": { "$ne": null }
}
```


The $ne operator means "not equal to." The query now looks for a user with the username "admin" whose password field is not equal to null. Since the password field for the admin user is a string (e.g., "secret"), it is not null, and the query returns a match, granting the attacker access without knowing the correct password. 
Injection exploit: Data leakage
An attacker can also use injection to leak all records in a collection. 
Attacker's input:
username: {"$gt": ""}
password: anything

What happens behind the scenes:
The application uses the input to build the query document.
The resulting MongoDB query becomes:
```json
{
  "username": { "$gt": "" },
  "password": "anything"
}
```


The $gt operator means "greater than." The query now searches for all users where the username string is "greater than" an empty string. This condition is true for every username, so the query returns all user records from the database, not just a specific one. 

**How to prevent PyMongo injection**  
The best way to prevent this vulnerability is to ensure user input is never used directly to construct query operators. 
1. Cast input to the expected type
This is the simplest and most effective defense. If you expect a string, ensure that the input is treated as a string, not as a nested document. 
```python
from pymongo import MongoClient
from flask import Flask, request

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client.test_database

# Secure route
@app.route('/secure_login', methods=['POST'])
def secure_login():
    username = str(request.form.get('username')) # Cast to string
    password = str(request.form.get('password')) # Cast to string
    
    # Safe query where user input is treated as a string value
    user = db.users.find_one({
        'username': username,
        'password': password
    })
    
    if user:
        return 'Login successful!'
    else:
        return 'Invalid credentials'
```


2. Use a sanitization library
You can use a library like mongo-sanitize to recursively strip any keys that start with a $ from the input, preventing operator injection. 
bash
pip install mongo-sanitize


```python
from pymongo import MongoClient
from flask import Flask, request
from mongosanitizer.sanitizer import sanitize

# Secure route with sanitizer
@app.route('/sanitized_login', methods=['POST'])
def sanitized_login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Sanitize the user input before using it
    sanitized_input = sanitize({'username': username, 'password': password})
    
    user = db.users.find_one(sanitized_input)
    
    if user:
        return 'Login successful!'
    else:
        return 'Invalid credentials'
```

**How to prevent Nodejs monogo injection**  
bad code:  
```javascript
// client sends query like this: domain.com/api/users?email[$ne]=x
// some parsers...
console.log(req.query.email) // output -> { $ne: 'x'}
const user = await User.find({ email: req.query.email }); // boom! 
//it will fetch all users whose email is not "x"
```

good code:  
**Using Express Mongo Sanitize**  
Express Mongo Sanitize is a package that provides middleware to sanitize user input before it is used in a database query. It is designed specifically to prevent NoSQL injection attacks in Node.js applications that use MongoDB.
```bash
npm install express-mongo-sanitize
```

```javascript
const express = require('express');
const mongoSanitize = require('express-mongo-sanitize');
const mongoose = require('mongoose');
mongoose.connect('mongodb://localhost/myapp');
// Sanitize user input:
// With this middleware in place, any user input that is sent in the request body or query parameters will be automatically sanitized before being used in a MongoDB query.
app.use(mongoSanitize());
// Retrieve user information
app.get('/user', async (req, res) => {
  try {
    const user = await User.find({ email: req.query.email });
    res.json(user);
  } catch (err) {
    console.error(err);
    res.status(500).send('Server Error');
  }
});
```




