#include <string.h>
#include <stdio.h>

void secure_process_data_c(const char* user_input, size_t input_len) {
    char destination_buffer[128];

    // Determine the safe number of bytes to copy.
    size_t dest_size = sizeof(destination_buffer);
    size_t bytes_to_copy = (input_len < dest_size) ? input_len : dest_size;

    printf("Destination size is %zu. Input size is %zu. Copying %zu bytes.\n", 
           dest_size, input_len, bytes_to_copy);

    // This call is now safe. It will never write more than 128 bytes.
    memcpy(destination_buffer, user_input, bytes_to_copy);
}
