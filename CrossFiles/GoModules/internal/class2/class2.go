package class2

import (
	"database/sql"
	"fmt"

	_ "github.com/mattn/go-sqlite3"
)

type Class2 struct {
	input string
	db    *sql.DB
}

func New(input string) *Class2 {
	return &Class2{input: input}
}

func (c *Class2) ConnectDb(dbName string) error {
	var err error
	c.db, err = sql.Open("sqlite3", dbName)
	if err != nil {
		return fmt.Errorf("failed to connect to database: %v", err)
	}
	return nil
}

func (c *Class2) Process() {
	fmt.Printf("Class2 processing: %s\n", c.input)
	if c.db == nil {
		fmt.Println("Database not connected")
		return
	}

	query := fmt.Sprintf("SELECT * FROM users WHERE username = '%s'", c.input)
	fmt.Printf("Executing query: %s\n", query)

	rows, err := c.db.Query(query)
	if err != nil {
		fmt.Printf("Error executing query: %v\n", err)
		return
	}
	defer rows.Close()

	for rows.Next() {
		var username string
		if err := rows.Scan(&username); err != nil {
			fmt.Printf("Error scanning row: %v\n", err)
			return
		}
		fmt.Printf("Username: %s\n", username)
	}
}

func (c *Class2) CloseDb() {
	if c.db != nil {
		c.db.Close()
	}
}
