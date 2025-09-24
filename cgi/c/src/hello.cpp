#include <iostream>
#include <string>
#include <cstdlib>

int main() {
    // Set content type header
    std::cout << "Content-Type: text/html\r\n\r\n";
    
    // Get query string from environment
    char* query_string = getenv("QUERY_STRING");
    char* request_method = getenv("REQUEST_METHOD");
    
    // Start HTML output
    std::cout << "<!DOCTYPE html>\n";
    std::cout << "<html>\n";
    std::cout << "<head><title>CGI Example</title></head>\n";
    std::cout << "<body>\n";
    std::cout << "<h1>Hello from CGI!</h1>\n";
    
    // Display request information
    std::cout << "<h2>Request Information:</h2>\n";
    std::cout << "<p><strong>Method:</strong> " 
              << (request_method ? request_method : "Unknown") << "</p>\n";
    std::cout << "<p><strong>Query String:</strong> " 
              << (query_string ? query_string : "None") << "</p>\n";
    
    // Simple form
    std::cout << "<h2>Test Form:</h2>\n";
    std::cout << "<form method=\"GET\">\n";
    std::cout << "<label>Name: <input type=\"text\" name=\"name\"></label><br><br>\n";
    std::cout << "<label>Age: <input type=\"number\" name=\"age\"></label><br><br>\n";
    std::cout << "<input type=\"submit\" value=\"Submit\">\n";
    std::cout << "</form>\n";
    
    // Parse and display form data if present
    if (query_string && strlen(query_string) > 0) {
        std::cout << "<h2>Form Data Received:</h2>\n";
        std::cout << "<pre>" << query_string << "</pre>\n";
    }
    
    std::cout << "</body>\n";
    std::cout << "</html>\n";
    
    return 0;
}
