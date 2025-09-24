#include <iostream>
#include <fstream>
#include <string>
#include <regex>
#include <vector>

class CGIAnalyzer {
private:
    std::vector<std::string> cgi_patterns = {
        R"(Content-Type:)",
        R"(getenv\s*\(\s*[\"']QUERY_STRING[\"'])",
        R"(getenv\s*\(\s*[\"']REQUEST_METHOD[\"'])",
        R"(getenv\s*\(\s*[\"']CONTENT_LENGTH[\"'])",
        R"(getenv\s*\(\s*[\"']HTTP_)",
        R"(getenv\s*\(\s*[\"']SERVER_)",
        R"(getenv\s*\(\s*[\"']REMOTE_)",
        R"(<form)",
        R"(application/x-www-form-urlencoded)",
        R"(multipart/form-data)"
    };
    
    std::vector<std::string> pattern_names = {
        "HTTP Content-Type header",
        "QUERY_STRING environment variable",
        "REQUEST_METHOD environment variable", 
        "CONTENT_LENGTH environment variable",
        "HTTP_ environment variables",
        "SERVER_ environment variables",
        "REMOTE_ environment variables",
        "HTML form elements",
        "Form URL encoding",
        "Multipart form data"
    };

public:
    void analyzeFile(const std::string& filename) {
        std::ifstream file(filename);
        if (!file.is_open()) {
            std::cerr << "Error: Cannot open file " << filename << std::endl;
            return;
        }
        
        std::string content((std::istreambuf_iterator<char>(file)),
                           std::istreambuf_iterator<char>());
        file.close();
        
        std::cout << "CGI Analysis for: " << filename << std::endl;
        std::cout << "================================" << std::endl;
        
        int cgi_score = 0;
        
        for (size_t i = 0; i < cgi_patterns.size(); ++i) {
            std::regex pattern(cgi_patterns[i], std::regex::icase);
            if (std::regex_search(content, pattern)) {
                std::cout << "✓ Found: " << pattern_names[i] << std::endl;
                cgi_score++;
            }
        }
        
        std::cout << std::endl;
        std::cout << "CGI Score: " << cgi_score << "/" << cgi_patterns.size() << std::endl;
        
        if (cgi_score >= 2) {
            std::cout << "Verdict: LIKELY a CGI program" << std::endl;
        } else if (cgi_score == 1) {
            std::cout << "Verdict: POSSIBLY a CGI program" << std::endl;
        } else {
            std::cout << "Verdict: UNLIKELY to be a CGI program" << std::endl;
        }
    }
};

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cout << "Usage: " << argv[0] << " <source_file>" << std::endl;
        return 1;
    }
    
    CGIAnalyzer analyzer;
    analyzer.analyzeFile(argv[1]);
    
    return 0;
}
