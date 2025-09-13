#include <string>
#include <iostream>
#include <cstring>

class User {
public:
    int id;
    std::string name;

    User(int i, const std::string& n) : id(i), name(n) {
        std::cout << "User '" << name << "' constructed." << std::endl;
    }
    ~User() {
        std::cout << "User '" << name << "' destructed." << std::endl;
    }
};

int main() {
    User user1(1, "Alice");
    User user2(2, "Bob");

    // DANGER: This is a shallow copy.
    // It copies the pointer inside user1.name, not the string data itself.
    memcpy(&user2, &user1, sizeof(User)); 
    // Now user1.name and user2.name point to the SAME memory.
    // user2's original string is leaked.

    std::cout << "After memcpy, user2's name is: " << user2.name << std::endl;
    
    return 0; // CRASH or DOUBLE FREE!
    // When main ends, both user1 and user2's destructors will try to free
    // the SAME memory for the string "Alice", leading to a crash.

    // ✅ The Correct Way: Use the C++ copy constructor or copy assignment operator.
    // This correctly invokes the std::string copy assignment operator.
    // user2 = user1;


}
