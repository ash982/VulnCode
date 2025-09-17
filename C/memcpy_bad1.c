#include <string.h>

int main() {
    char buffer[] = "123456789";
    
    // DANGER: We want to shift "456789" to the start of the buffer.
    // The source (buffer + 3) and destination (buffer) overlap.
    // This is UNDEFINED BEHAVIOR.
    memcpy(buffer, buffer + 3, 6); // Don't do this!
    
    // ✅ The Correct Way: Use memmove
    // memmove is specifically designed to handle overlapping memory correctly.
    memmove(buffer, buffer + 3, 6);
    
    return 0;
}
