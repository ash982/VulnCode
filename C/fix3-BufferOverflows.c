#include <string.h>
#include <stdio.h>
#include <stdbool.h> // For bool in C

// Returns true on success, false on failure.
bool secure_process_data_guard(const char* user_input, size_t input_len) {
    char destination_buffer[128];
    size_t dest_size = sizeof(destination_buffer);

    // GUARD CONDITION: Check if the input will fit.
    if (input_len > dest_size) {
        fprintf(stderr, "ERROR: Input size (%zu) exceeds destination capacity (%zu).\n", 
                input_len, dest_size);
        return false; // Abort the operation.
    }

    // If we get here, we know the copy is safe.
    memcpy(destination_buffer, user_input, input_len);
    printf("Successfully copied %zu bytes.\n", input_len);
    return true;
}
