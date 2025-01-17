#ifndef CLASS1_H
#define CLASS1_H

#include <string>

class Class1 {
private:
    std::string input;

public:
    Class1(const std::string& input);
    void process();
};

#endif
