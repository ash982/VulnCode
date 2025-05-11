package main

import (
	"encoding/xml"
	"fmt"
	"io"
	"os"
	"strings"
)

func main() {
	// XML with external entity
	xxeXML := `
<!DOCTYPE test [
	<!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<test>&xxe;</test>
`

	fmt.Println("=== Attempt 1: Basic XXE attempt via Unmarshal()===")
	attemptXXEUnmarshal(xxeXML)

	fmt.Println("\n=== Attempt 2: Using a custom entity map ===")
	attemptCustomEntityXXE(xxeXML)

	fmt.Println("\n=== Attempt 3: Using TokenReader to see raw entity reference ===")
	tokenizeXXEAttempt(xxeXML)

	fmt.Println("\n=== Attempt 4: Try to trick parser with nested entities ===")
	nestedXXE := `
<!DOCTYPE test [
	<!ENTITY % file SYSTEM "file:///etc/passwd">
	<!ENTITY xxe "%file;">
]>
<test>&xxe;</test>
`
	attemptXXEUnmarshal(nestedXXE)

	fmt.Println("\n=== For comparison: Successfully processing a custom entity ===")
	safeXML := `<test>&custom;</test>`
	decoder := xml.NewDecoder(strings.NewReader(safeXML))
	decoder.Entity = map[string]string{
		"custom": "This works because it's explicitly defined",
	}

	var result struct {
		Content string `xml:",chardata"`
	}

	err := decoder.Decode(&result)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
	} else {
		fmt.Printf("Custom entity content: %q\n", result.Content)
	}

	// Check if /etc/passwd exists and print first few lines directly
	// This is to show that the file exists but Go's XML parser won't access it
	fmt.Println("\n=== Direct file access (NOT through XML) for comparison ===")
	checkFileDirectly("/etc/passwd")
}

func attemptXXEUnmarshal(xmlData string) {
	var result struct {
		Content string `xml:",chardata"`
	}

	err := xml.Unmarshal([]byte(xmlData), &result)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
	} else {
		fmt.Printf("Content: %q\n", result.Content)
		if result.Content == "" {
			fmt.Println("Note: Content is empty because XXE was blocked")
		}
	}
}

func attemptCustomEntityXXE(xmlData string) {
	var result struct {
		Content string `xml:",chardata"`
	}

	decoder := xml.NewDecoder(strings.NewReader(xmlData))
	// Attempt to define xxe entity ourselves
	decoder.Entity = map[string]string{
		"xxe": "My custom xxe value (but external entity still won't be processed)",
	}

	err := decoder.Decode(&result)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
	} else {
		fmt.Printf("Content with custom entity map: %q\n", result.Content)
	}
}

func tokenizeXXEAttempt(xmlData string) {
	decoder := xml.NewDecoder(strings.NewReader(xmlData))

	for {
		token, err := decoder.Token()
		if err == io.EOF {
			break
		}
		if err != nil {
			fmt.Printf("Token error: %v\n", err)
			break
		}

		fmt.Printf("Token type: %T\n", token)

		switch t := token.(type) {
		case xml.StartElement:
			fmt.Printf("  Start Element: %s\n", t.Name.Local)
		case xml.EndElement:
			fmt.Printf("  End Element: %s\n", t.Name.Local)
		case xml.CharData:
			fmt.Printf("  Character Data: %q\n", string(t))
		case xml.Comment:
			fmt.Printf("  Comment: %s\n", t)
		case xml.Directive:
			fmt.Printf("  Directive: %s\n", t)
		case xml.ProcInst:
			fmt.Printf("  Processing Instruction: %s\n", t)
		}
	}
}

func checkFileDirectly(filepath string) {
	// This function directly reads the file to show it exists
	// and is accessible by the program directly (not through XML)
	file, err := os.Open(filepath)
	if err != nil {
		fmt.Printf("Could not open %s: %v\n", filepath, err)
		return
	}
	defer file.Close()

	// Read just the first 200 bytes
	buffer := make([]byte, 200)
	n, err := file.Read(buffer)
	if err != nil && err != io.EOF {
		fmt.Printf("Error reading file: %v\n", err)
		return
	}

	fmt.Printf("First %d bytes of %s (direct file access):\n%s\n",
		n, filepath, buffer[:n])
	fmt.Println("Note: This direct file access works, but XML external entity won't access the file")
}
