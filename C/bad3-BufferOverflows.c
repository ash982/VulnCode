#include <string.h>

void process_request(const char* input_data, size_t input_len) {
    char dest_buffer[64];

    // DANGER: What if input_len is greater than 64?
    // This will write past the end of dest_buffer, corrupting the stack.
    memcpy(dest_buffer, input_data, input_len);


    // ✅ The Correct Way: Always validate the size before copying.
    // #include <string.h>
    // #include <algorithm> // for std::min in C++
    
    // void process_request(const char* input_data, size_t input_len) {
    //     char dest_buffer[64];
        
    //     // Calculate the safe amount to copy.
    //     size_t len_to_copy = (input_len < sizeof(dest_buffer)) ? input_len : sizeof(dest_buffer);
    //     // In C++: size_t len_to_copy = std::min(input_len, sizeof(dest_buffer));
    
    //     memcpy(dest_buffer, input_data, len_to_copy);
    // }

    // ✅ For a safer alternative, consider memcpy_s if your platform supports it (part of C11 Annex K).


}
