package main

import (
	"encoding/xml"
	"fmt"
	"strings"
)

func main() {
	// Safe XML
	//xmlData := `<root><element>This is a test with &myentity;</element></root>`

	//Insafe XML: blocked, error decoding XML: XML syntax error on line 5: invalid character entity &xxe;
	xmlData := `
	<!DOCTYPE test [
		<!ENTITY xxe SYSTEM "file:///etc/passwd">
	]>
	<test>&xxe;</test>
	`

	decoder := xml.NewDecoder(strings.NewReader(xmlData))
	// the entity map is just string substitutions
	decoder.Entity = map[string]string{
		"myentity": "file:///etc/passwd",
	}

	type Element struct {
		Value string `xml:",chardata"`
	}

	type Root struct {
		Element Element `xml:"element"`
	}

	var root Root
	err := decoder.Decode(&root)
	if err != nil {
		fmt.Println("Error decoding XML:", err)
		return
	}

	fmt.Printf("Decoded value: %s\n", root.Element.Value)
}
