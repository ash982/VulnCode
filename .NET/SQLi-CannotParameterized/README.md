Several SQL elements require whitelist validation because they can't be safely parameterized. Here are the key ones:

**1. ORDER BY Clauses**
```c#
-- Vulnerable - can't parameterize column names
ORDER BY @sortField ASC  -- Won't work as intended

-- Must whitelist:
ORDER BY name ASC  -- Column name must be validated
```

**2. Column Names in SELECT**
```c#
// Vulnerable - if user controls which columns to select
string sql = $"SELECT {userSelectedColumns} FROM users";

// Safe approach:
var allowedColumns = new[] { "id", "name", "email", "created_date" };
var validColumns = userSelectedColumns.Split(',')
    .Where(col => allowedColumns.Contains(col.Trim().ToLower()));
```
DynamicSelect.cs

**3. Table Names**
```c#
// Vulnerable
string sql = $"SELECT * FROM {tableName}";

// Safe - whitelist tables
var allowedTables = new[] { "users", "products", "orders" };
if (!allowedTables.Contains(tableName.ToLower()))
    throw new ArgumentException("Invalid table name");
```
DynamicTableQuery.cs

**4. GROUP BY Fields**
```c#
-- Same issue as ORDER BY
GROUP BY @groupField  -- Won't work
GROUP BY category     -- Must validate column exists
```

**5. Database/Schema Names**
```c#
// Vulnerable
string sql = $"SELECT * FROM {schemaName}.users";

// Safe - validate against allowed schemas
var allowedSchemas = GetAllowedSchemasForUser(currentUser);
if (!allowedSchemas.Contains(schemaName))
    throw new UnauthorizedAccessException();
```
MultiTenantQuery.cs

**6. LIMIT/OFFSET in Dynamic Queries**
```c#
// Less critical but validate ranges
if (pageSize > 1000 || pageSize < 1)
    throw new ArgumentException("Invalid page size");
    
if (offset < 0)
    throw new ArgumentException("Invalid offset");
```
PaginationQuery.cs

**7. JOIN Conditions (Column Names)**
```c#
-- When JOIN conditions are dynamic
JOIN table2 ON table1.id = table2.user_id  -- Column names need validation
```

**8. Index Hints (MySQL)**
```c#
-- MySQL specific
SELECT * FROM users USE INDEX (idx_name)  -- Index name needs validation
```

**9. CASE/WHEN Column References**
```c#
-- When building dynamic CASE statements
CASE 
    WHEN status = 'active' THEN priority  -- Column names need validation
END
```

**General Rule**
Any SQL element that affects query structure (not just data) needs whitelist validation:
```c#
public class SqlStructureValidator
{
    // These all need whitelisting:
    public static readonly string[] StructuralElements = 
    {
        "Column names",
        "Table names", 
        "Schema names",
        "Index names",
        "Sort directions",
        "Aggregate functions (if dynamic)",
        "Window function parameters"
    };
}
```

SqlElementValidator.cs

**Safe Pattern**
```c#
public string BuildSafeQuery(QueryParams parameters)
{
    // 1. Validate all structural elements
    ValidateColumnName(parameters.SortField);
    ValidateTableName(parameters.TableName);
    ValidateDirection(parameters.SortDirection);
    
    // 2. Build structure safely
    var sql = $@"
        SELECT {GetValidatedColumns(parameters.Columns)}
        FROM {GetValidatedTable(parameters.TableName)}
        WHERE status = @status  -- This CAN be parameterized
        ORDER BY {parameters.SortField} {parameters.SortDirection}";
    
    // 3. Parameterize the data values
    cmd.Parameters.Add("@status", parameters.StatusFilter);
    
    return sql;
}
```
SafeQueryBuilder.cs

**The key insight: Structure = Validate, Data = Parameterize**
