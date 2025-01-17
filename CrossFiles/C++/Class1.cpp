#include "Class1.h"
#include <iostream>
#include <cstdlib>

Class1::Class1(const std::string& input) : input(input) {}

void Class1::process() {
    std::cout << "Class1 processing: " << input << std::endl;
    // Potentially unsafe operation
    std::string command = "echo " + input;
    system(command.c_str());
}
