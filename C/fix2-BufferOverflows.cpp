#include <cstring>
#include <iostream>
#include <algorithm> // Required for std::min

void secure_process_data_cpp(const char* user_input, size_t input_len) {
    char destination_buffer[128];

    // std::min makes the intent clear.
    size_t bytes_to_copy = std::min(input_len, sizeof(destination_buffer));

    std::cout << "Destination size is " << sizeof(destination_buffer)
              << ". Input size is " << input_len
              << ". Copying " << bytes_to_copy << " bytes." << std::endl;

    // This call is safe.
    memcpy(destination_buffer, user_input, bytes_to_copy);
}
