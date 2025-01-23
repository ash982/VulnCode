package main

import (
	"fmt"
	"os"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: go run main.go <input>")
		return
	}

	taintedInput := os.Args[1]

	obj1 := NewClass1(taintedInput)
	obj2 := NewClass2(taintedInput)

	obj1.Process()
	obj2.Process()
}
