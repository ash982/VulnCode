package main

import (
	"fmt"
	"os"

	"github.com/myproject/internal/class1"
	"github.com/myproject/internal/class2"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: go run main.go <input>")
		return
	}

	taintedInput := os.Args[1]
	obj1 := class1.New(taintedInput)
	obj2 := class2.New(taintedInput)

	obj1.Process()

	if err := obj2.ConnectDb("mydb.sqlite"); err != nil {
		fmt.Printf("Failed to connect to database: %v\n", err)
		return
	}
	defer obj2.CloseDb()

	obj2.Process()
}
