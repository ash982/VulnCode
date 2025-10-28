## Knex.js  
SQL query builder for PostgreSQL, CockroachDB, MSSQL, MySQL, MariaDB, SQLite3, Better-SQLite3, Oracle, and Amazon Redshift designed to be flexible, portable, 
and fun to use.  

It features both traditional node style callbacks as well as a promise interface for cleaner async flow control, a stream interface, full-featured query and 
schema builders, transaction support (with savepoints), connection pooling and standardized responses between different query clients and dialects.  

https://knexjs.org/  

CVE-2016-20018: Limited SQL injection via WHERE clause
This vulnerability is present in Knex.js versions up to 2.3.0 when used with a MySQL database. 
Vulnerability: The bug arose because Knex.js failed to properly handle certain object and array inputs in the where() clause. An attacker could craft a malicious input that allowed them to override or ignore the WHERE clause entirely.
Impact: Attackers could bypass filters and retrieve records from a database table that they were not authorized to access.
Fix: The vulnerability was patched in Knex.js version 2.4.0. Users should update to the latest version to mitigate this risk. 
CVE-2019-10757: SQL injection via MSSQL dialect
This vulnerability affected Knex.js versions before 0.19.5 when used with the MSSQL dialect. 
Vulnerability: It was caused by incorrect escaping of identifiers, which allowed an attacker to craft a malicious query.
Fix: The issue was resolved in version 0.19.5. 
How to prevent SQL injection in Knex.js
Even with these CVEs patched, improper usage of Knex.js can still introduce vulnerabilities. Here are some best practices to follow:
Use parameter binding: Knex.js's native methods automatically use parameterized queries, which keeps user input separate from the SQL command. For example, use the object-based syntax for the where() clause:
javascript
knex('users').where({ id: userProvidedId }).select();
This is secure because the userProvidedId is passed to the database as a value, not as executable SQL.
Handle raw queries with care: When using knex.raw() to write custom SQL, always use bindings (? or ??) instead of string concatenation.
Secure:
javascript
knex.raw('SELECT * FROM users WHERE id = ?', [userProvidedId]);
Insecure (and vulnerable to SQL injection):
javascript
knex.raw(`SELECT * FROM users WHERE id = '${userProvidedId}'`);
Validate input types: Be cautious when accepting dynamic objects or arrays from user input. As seen in CVE-2016-20018, unexpected input types can be exploited. Implement server-side validation to ensure that user-provided data matches the expected type and format before passing it to your database queries.
Stay updated: Regularly update your knex.js package to the latest version to ensure you have all security patches. You can check for new vulnerabilities using tools like Snyk. 
