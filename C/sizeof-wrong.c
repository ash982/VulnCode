void my_buggy_copy(char* dest_ptr, const char* src_ptr, size_t src_len) {
    // BUG! sizeof(dest_ptr) is 8 (on a 64-bit system), not the buffer's actual size.
    // This check is completely broken and provides a false sense of security.
    size_t bytes_to_copy = (src_len < sizeof(dest_ptr)) ? src_len : sizeof(dest_ptr);
    memcpy(dest_ptr, src_ptr, bytes_to_copy); 
}

int main() {
    char my_buffer[256];
    char my_data[50];
    // This will only copy 8 bytes instead of 50 because of the bug.
    my_buggy_copy(my_buffer, my_data, 50);
}
