#include <stdio.h>
#include <string.h> // For memcpy and memset

//==================================================================
// THE SAFE FUNCTION
// It accepts a pointer AND the size of the memory that pointer points to.
// This function is designed for generic byte copying.
//==================================================================
void my_safe_copy(
    char* dest_ptr,          // The pointer to the destination
    size_t dest_size,        // The total capacity of the destination buffer
    const char* src_ptr,     // The pointer to the source data
    size_t src_len           // The number of bytes we want to copy from the source
) {
    printf("--- Inside my_safe_copy ---\n");
    printf("Function received a buffer of size %zu and wants to copy %zu bytes.\n", 
           dest_size, src_len);

    // This is the core safety check: determine the actual number of bytes to copy.
    // It's the smaller of the source length or the destination capacity.
    size_t bytes_to_copy = (src_len < dest_size) ? src_len : dest_size;

    printf("Check passed. Will copy %zu bytes.\n", bytes_to_copy);

    // Perform the safe copy. This will never write more than 'dest_size' bytes.
    memcpy(dest_ptr, src_ptr, bytes_to_copy);

    printf("--- Exiting my_safe_copy ---\n\n");
}


//==================================================================
// THE CALLER (main function)
// It owns the buffer and therefore knows its real size.
//==================================================================
int main() {
    // The caller creates the actual buffer on the stack.
    // Here, 'destination_buffer' is an array.
    char destination_buffer[100];
    
    // --- Scenario 1: Source data is smaller than the destination buffer ---
    printf("--- SCENARIO 1: Source fits in destination ---\n");
    const char* source1 = "This is a test string that fits perfectly.";
    size_t source1_len = strlen(source1);

    // Clear the buffer to ensure no garbage data from previous runs.
    memset(destination_buffer, 0, sizeof(destination_buffer));

    // The caller passes the buffer AND its size using sizeof().
    // This is the correct way to provide the size information.
    my_safe_copy(destination_buffer, sizeof(destination_buffer), source1, source1_len);

    // Note: We print with a specific length because memcpy doesn't null-terminate.
    printf("Result in destination: '%.*s'\n", (int)source1_len, destination_buffer);
    printf("--- END SCENARIO 1 ---\n\n");


    // --- Scenario 2: Source data is larger than the destination buffer ---
    printf("--- SCENARIO 2: Source is too large and will be truncated ---\n");
    const char* source2 = "This is a very long string that is definitely much larger than the destination buffer and therefore it must be truncated to fit safely without causing a buffer overflow.";
    size_t source2_len = strlen(source2);

    // Clear the buffer again.
    memset(destination_buffer, 0, sizeof(destination_buffer));

    // The call is identical. The safe function's internal logic will handle the truncation.
    my_safe_copy(destination_buffer, sizeof(destination_buffer), source2, source2_len);

    // We print only the number of bytes that would fit in the buffer.
    printf("Result in destination (truncated): '%.*s'\n", (int)sizeof(destination_buffer), destination_buffer);
    printf("--- END SCENARIO 2 ---\n\n");

    return 0;
}
