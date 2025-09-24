#include <iostream>
#include <fstream>
#include <string>
#include <regex>
#include <sys/stat.h>
#include <unistd.h>

class CGIDetector {
public:
    struct DetectionResult {
        bool isExecutable = false;
        bool hasHTTPHeaders = false;
        bool usesCGIEnvVars = false;
        bool producesHTML = false;
        bool respondsToInput = false;
        int confidenceScore = 0;
    };
    
    DetectionResult detectCGI(const std::string& filepath) {
        DetectionResult result;
        
        // Check if file is executable
        result.isExecutable = isExecutable(filepath);
        
        // If it's a source file, analyze source code
        if (filepath.find(".cpp") != std::string::npos || 
            filepath.find(".c") != std::string::npos) {
            analyzeSourceCode(filepath, result);
        } else if (result.isExecutable) {
            // If it's a binary, test runtime behavior
            testRuntimeBehavior(filepath, result);
        }
        
        // Calculate confidence score
        calculateConfidence(result);
        
        return result;
    }
    
private:
    bool isExecutable(const std::string& filepath) {
        struct stat sb;
        return (stat(filepath.c_str(), &sb) == 0) && (sb.st_mode & S_IXUSR);
    }
    
    void analyzeSourceCode(const std::string& filepath, DetectionResult& result) {
        std::ifstream file(filepath);
        if (!file.is_open()) return;
        
        std::string content((std::istreambuf_iterator<char>(file)),
                           std::istreambuf_iterator<char>());
        
        // Check for HTTP headers
        if (std::regex_search(content, std::regex(R"(Content-Type:)", std::regex::icase))) {
            result.hasHTTPHeaders = true;
        }
        
        // Check for CGI environment variables
        if (std::regex_search(content, std::regex(R"(getenv.*QUERY_STRING|getenv.*REQUEST_METHOD)", std::regex::icase))) {
            result.usesCGIEnvVars = true;
        }
        
        // Check for HTML output
        if (std::regex_search(content, std::regex(R"(<html|<body|text/html)", std::regex::icase))) {
            result.producesHTML = true;
        }
    }
    
    void testRuntimeBehavior(const std::string& filepath, DetectionResult& result) {
        // This would require actually executing the program
        // For safety, we'll just mark it as potential CGI if executable
        result.respondsToInput = true; // Placeholder
    }
    
    void calculateConfidence(DetectionResult& result) {
        int score = 0;
        if (result.isExecutable) score += 10;
        if (result.hasHTTPHeaders) score += 30;
        if (result.usesCGIEnvVars) score += 40;
        if (result.producesHTML) score += 15;
        if (result.respondsToInput) score += 5;
        
        result.confidenceScore = score;
    }
};

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cout << "Usage: " << argv[0] << " <file_to_analyze>" << std::endl;
        return 1;
    }
    
    CGIDetector detector;
    auto result = detector.detectCGI(argv[1]);
    
    std::cout << "CGI Detection Results for: " << argv[1] << std::endl;
    std::cout << "========================================" << std::endl;
    std::cout << "Executable: " << (result.isExecutable ? "Yes" : "No") << std::endl;
    std::cout << "HTTP Headers: " << (result.hasHTTPHeaders ? "Yes" : "No") << std::endl;
    std::cout << "CGI Env Vars: " << (result.usesCGIEnvVars ? "Yes" : "No") << std::endl;
    std::cout << "HTML Output: " << (result.producesHTML ? "Yes" : "No") << std::endl;
    std::cout << "Confidence Score: " << result.confidenceScore << "/100" << std::endl;
    
    if (result.confidenceScore >= 70) {
        std::cout << "Verdict: DEFINITELY a CGI program" << std::endl;
    } else if (result.confidenceScore >= 40) {
        std::cout << "Verdict: LIKELY a CGI program" << std::endl;
    } else if (result.confidenceScore >= 20) {
        std::cout << "Verdict: POSSIBLY a CGI program" << std::endl;
    } else {
        std::cout << "Verdict: UNLIKELY to be a CGI program" << std::endl;
    }
    
    return
