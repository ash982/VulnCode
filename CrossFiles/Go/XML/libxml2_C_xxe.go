package main

// #cgo pkg-config: libxml-2.0
// #include <libxml/parser.h>
// #include <libxml/tree.h>
import "C"
import (
	"fmt"
	"unsafe"
)

func main() {
	// Initialize libxml2
	C.xmlInitParser()
	defer C.xmlCleanupParser()

	xmlStr := C.CString(`<!DOCTYPE doc [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
	<root>
		<data>&xxe;</data>
	</root>`)
	defer C.free(unsafe.Pointer(xmlStr))

	// Secure: Parse the XML document without entity substitution by default
	// doc := C.xmlReadMemory(xmlStr, C.int(len(C.GoString(xmlStr))), nil, nil, 0)

	// Insecure: Parse untrusted XML with entity substitution enabled
	// XML_PARSE_NOENT: this option enables substitution of entities
	// XML_PARSE_NO_XXE: option to disables loading of external DTDs or entities.
	// XML_PARSE_NONET: Disable network access with the built-in HTTP or FTP clients (no external entity)
	// XML_PARSE_NOENT | XML_PARSE_NONET: only allow internal entity substitution
	
	doc := C.xmlReadMemory(
		xmlStr,                         // XML string
		C.int(len(C.GoString(xmlStr))), // Length of XML string
		nil,                            // URL (optional)
		nil,                            // Encoding (optional)
		C.XML_PARSE_NOENT,              // Enables substitution of entities (both internal and external)
	)
	if doc == nil {
		fmt.Println("Error parsing XML")
		return
	}
	defer C.xmlFreeDoc(doc)

	// Get the root element
	root := C.xmlDocGetRootElement(doc)
	if root == nil {
		fmt.Println("Error: No root element")
		return
	}

	// Find the first child node named "data"
	for child := root.children; child != nil; child = child.next {
		if C.GoString((*C.char)(unsafe.Pointer(child.name))) == "data" {
			// Print the content of the "data" node
			if child.children != nil && child.children.content != nil {
				fmt.Printf("Value: %s\n", C.GoString((*C.char)(unsafe.Pointer(child.children.content))))
			}
			break
		}
	}
}
