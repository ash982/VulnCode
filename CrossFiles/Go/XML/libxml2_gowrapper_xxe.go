package main

import (
	"fmt"
	"strings"

	"github.com/lestrrat-go/libxml2/parser"
)

func main() {
	xmlContent := `<!DOCTYPE doc [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
	<root>
		<data>&xxe;</data>
	</root>`

	//XMLParseNoEnt: enable parsing of external entities during XML parsing. This is vulnerable XML External Entity (XXE) attacks.
	p := parser.New(parser.XMLParseNoEnt)
	doc, err := p.ParseReader(strings.NewReader(xmlContent))
	if err != nil {
		fmt.Println("Error parsing XML:", err)
		return
	}
	defer doc.Free()

	// The content of &xxe; will not be expanded, preventing potential security issues.
	root, err := doc.DocumentElement()
	fmt.Println("Root element:", root.NodeValue())
}
