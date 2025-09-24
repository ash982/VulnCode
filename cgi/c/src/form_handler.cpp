#include <iostream>
#include <string>
#include <map>
#include <sstream>
#include <cstdlib>
#include <algorithm>

class CGIHandler {
private:
    std::map<std::string, std::string> params;
    
    std::string urlDecode(const std::string& str) {
        std::string result;
        for (size_t i = 0; i < str.length(); ++i) {
            if (str[i] == '+') {
                result += ' ';
            } else if (str[i] == '%' && i + 2 < str.length()) {
                int value;
                std::istringstream is(str.substr(i + 1, 2));
                if (is >> std::hex >> value) {
                    result += static_cast<char>(value);
                    i += 2;
                } else {
                    result += str[i];
                }
            } else {
                result += str[i];
            }
        }
        return result;
    }
    
    void parseQueryString(const std::string& query) {
        std::istringstream iss(query);
        std::string pair;
        
        while (std::getline(iss, pair, '&')) {
            size_t eq_pos = pair.find('=');
            if (eq_pos != std::string::npos) {
                std::string key = urlDecode(pair.substr(0, eq_pos));
                std::string value = urlDecode(pair.substr(eq_pos + 1));
                params[key] = value;
            }
        }
    }
    
public:
    CGIHandler() {
        char* method = getenv("REQUEST_METHOD");
        
        if (method && std::string(method) == "POST") {
            char* content_length_str = getenv("CONTENT_LENGTH");
            if (content_length_str) {
                int content_length = atoi(content_length_str);
                std::string post_data;
                post_data.resize(content_length);
                std::cin.read(&post_data[0], content_length);
                parseQueryString(post_data);
            }
        } else {
            char* query_string = getenv("QUERY_STRING");
            if (query_string) {
                parseQueryString(std::string(query_string));
            }
        }
    }
    
    std::string getParam(const std::string& key) {
        auto it = params.find(key);
        return (it != params.end()) ? it->second : "";
    }
    
    void printHeaders() {
        std::cout << "Content-Type: text/html\r\n\r\n";
    }
    
    void printHTML() {
        std::cout << "<!DOCTYPE html>\n";
        std::cout << "<html>\n";
        std::cout << "<head><title>Advanced CGI Form Handler</title></head>\n";
        std::cout << "<body>\n";
        std::cout << "<h1>Form Handler</h1>\n";
        
        std::string name = getParam("name");
        std::string email = getParam("email");
        std::string message = getParam("message");
        
        if (!name.empty() || !email.empty() || !message.empty()) {
            std::cout << "<h2>Submitted Data:</h2>\n";
            std::cout << "<p><strong>Name:</strong> " << name << "</p>\n";
            std::cout << "<p><strong>Email:</strong> " << email << "</p>\n";
            std::cout << "<p><strong>Message:</strong> " << message << "</p>\n";
            std::cout << "<hr>\n";
        }
        
        std::cout << "<h2>Contact Form:</h2>\n";
        std::cout << "<form method=\"POST\">\n";
        std::cout << "<table>\n";
        std::cout << "<tr><td>Name:</td><td><input type=\"text\" name=\"name\" required></td></tr>\n";
        std::cout << "<tr><td>Email:</td><td><input type=\"email\" name=\"email\" required></td></tr>\n";
        std::cout << "<tr><td>Message:</td><td><textarea name=\"message\" rows=\"4\" cols=\"50\" required></textarea></td></tr>\n";
        std::cout << "<tr><td colspan=\"2\"><input type=\"submit\" value=\"Submit\"></td></tr>\n";
        std::cout << "</table>\n";
        std::cout << "</form>\n";
        
        std::cout << "</body>\n";
        std::cout << "</html>\n";
    }
};

int main() {
    CGIHandler handler;
    handler.printHeaders();
    handler.printHTML();
    return 0;
}
