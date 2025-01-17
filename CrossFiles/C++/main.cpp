#include <iostream>
#include "Class1.h"
#include "Class2.h"

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cout << "Usage: " << argv[0] << " <input>" << std::endl;
        return 1;
    }

    std::string taintedInput = argv[1];

    Class1 obj1(taintedInput);
    Class2 obj2(taintedInput);

    obj1.process();
    obj2.process();

    return 0;
}
