-- Example using T-SQL (SQL Server)
CREATE PROCEDURE GetTableData (@TableName VARCHAR(100))
AS
BEGIN
    DECLARE @SQLQuery NVARCHAR(MAX);
    SET @SQLQuery = N'SELECT * FROM ' + QUOTENAME(@TableName);
    EXEC sp_executesql @SQLQuery; -- Executes the constructed SQL string
END
