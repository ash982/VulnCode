## File Extensions
The most common and generic file extension for both SQL template files and SQL stored procedure files (before they are deployed to the database) is simply:

`.sql`

While .sql is the universal convention, some specialized or vendor-specific extensions might be used to indicate the file's content or procedural language.

**💾 Stored Procedure File Extensions**

The file that contains the CREATE PROCEDURE script is typically named with a .sql extension.

However, in specific database environments, you might see:

`.spsql` (for SQL Stored Procedure, sometimes seen in IBM/Db2 environments)

`.pls` (in Oracle for PL/SQL procedural code, which includes procedures and functions)

`.prc` (sometimes used informally to denote a file containing a procedure)

Regardless of the extension, a stored procedure file is identifiable by the presence of a `CREATE PROCEDURE` or `CREATE` OR `REPLACE PROCEDURE` statement 
at the beginning of the script.

**📝 SQL Template File Extensions**
SQL template files almost universally use the .sql extension.

Because a template file is simply a text file with placeholders, it's often distinguished not by its extension, but by the templating language it uses, such as:

`.sql` (Plain SQL with placeholders like `{name}` or `$name`)

`.sql` `.j2` or `.j2` (if it uses the **Jinja2** templating engine)

`.sql` `.erb` (if it uses **ERB** in Ruby/Rails projects)

Ultimately, both files are essentially plain-text SQL scripts until the procedure is saved in the database or the template is used to generate a final query.

**The core difference lies in their purpose and where the code is executed or used:**

That's a great way to summarize the differences\! Here is the table in a format suitable for a **README.md** file:


## ⚖️ SQL Template vs. Stored Procedure: Core Differences

| Feature | SQL Stored Procedure File | SQL Template File |
| :--- | :--- | :--- |
| **Purpose** | Contains a set of SQL statements and procedural logic **designed to be stored, compiled, and executed on the database server.** | Contains a **boilerplate SQL script with placeholders** (parameters) designed to be filled in and executed elsewhere. |
| **Execution Location** | Executed directly on the **database server** (using `EXECUTE` or `CALL`). | Not executed directly; the final, filled-in script is usually executed **from an application** or a tool. |
| **Compilation/Storage** | The script is sent to the database, where it is **parsed, compiled** (creating an execution plan), and **saved as a database object**. | The file itself is **not stored in the database** as an object; it's a file on a file system or within an application's code base. |
| **Dynamic Content** | Contains **procedural logic** (e.g., `IF/ELSE`, `WHILE` loops, variables, error handling) and accepts **parameters** for dynamic execution. | Used to generate **dynamic SQL** by replacing placeholders with values or code snippets **before** sending the script to the database. |

## 🎯 Key Distinctions Explained
**Stored Procedure File**
A stored procedure file contains the SQL code (often vendor-specific extensions like T-SQL or PL/SQL) needed to create a database object (the stored procedure). 
Once executed, the code block is compiled and saved on the database server.

1. Pre-Compiled & Server-Side: Since it's saved in the database, the execution plan is often pre-compiled and cached, leading to better performance for
   repeated use. The logic runs entirely within the database environment.

3. Encapsulates Business Logic: They are used to implement complex, reusable business logic, enforce security (by granting permissions only on the procedure,
   not the underlying tables), and reduce network traffic (by sending one command instead of many SQL statements).

5. Security: Using parameters in stored procedures is a standard way to prevent SQL injection attacks.

**SQL Template File**
A SQL template file is a generic file containing valid SQL syntax, but with designated spots for substitution. It is a **design pattern** or boilerplate.

1. Code Generation: The primary purpose is to allow an external program (like an application, script, or development tool) to **programmatically generate**
   a final, runnable SQL query by injecting specific values, column names, or even entire clauses into the placeholders.

3. Flexibility: They offer flexibility where the structure of the SQL might need minor, controlled variations that a fixed stored procedure can't easily
   accommodate.

5. Not a Database Object: The template file itself is not "known" to the database; it's just a text file used by the client/application layer.

## Is it possible that stored procedure contain `{name}` or `$name` ?
Possible. In standard SQL stored procedure code, it is not possible to use generic template placeholders like `{name}` or `$name` in the way a templating engine 
(like Jinja or a Python script) uses them.

The database engine would interpret those characters literally, likely leading to a syntax error or treating it as a column/variable name 
that hasn't been defined correctly.

Here's how stored procedures handle **dynamic values**:
**1. Using Standard Stored Procedure Parameters**
A stored procedure uses its own formal input parameters (variables) defined in the `CREATE PROCEDURE` statement, typically prefixed with `@` (SQL Server, Sybase) 
or having no special prefix (MySQL, PostgreSQL) or being declared with a mode like `IN` or `OUT` (Oracle).

| Context |	Syntax for an Input Parameter	| Example Usage in the Code
| :--- | :--- | :--- |
| SQL Server (T-SQL) |	`@name` |	`SELECT * FROM Employees WHERE LastName = @name;`
| MySQL / MariaDB |	No prefix needed in definition/body |	`SELECT * FROM Employees WHERE LastName = name_param;`
| Oracle (PL/SQL) |	No prefix needed in definition/body |	`SELECT column INTO variable FROM Employees WHERE LastName = name_param;`

When calling the procedure, you pass the value for this defined parameter:
`EXECUTE GetEmployeeDetails 'Smith';`

**2. Using Dynamic SQL (The Exception)**
The only way to get the functionality of a template placeholder (where you're substituting a table name, a column name, or part of the SQL structure) is 
by using **Dynamic SQL inside the stored procedure**.

In this scenario:
The stored procedure accepts a standard **parameter** (e.g., `@TableName VARCHAR(100)`).
The stored procedure builds a full SQL query as a string by concatenating the parameter value with the rest of the SQL: `storedprecedure.sql`


Crucially, in the code above, the placeholder logic is handled by the procedural code logic (SET @SQLQuery = ...), not by the database engine's syntax for 
stored procedures itself.

**Security Note: Dynamic SQL is a known security risk for SQL Injection if the input is not rigorously validated or used with safe functions like QUOTENAME() 
(as shown above).**


