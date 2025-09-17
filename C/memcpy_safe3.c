#include <string.h>

// Assume PacketHeader is a POD struct
typedef struct { uint32_t packet_id; uint32_t data_len; } PacketHeader;

void handle_packet(const char* buffer) {
    PacketHeader header;
    
    // Copy the first part of the buffer into our header struct to "deserialize" it.
    memcpy(&header, buffer, sizeof(PacketHeader));

    // Now we can use header.packet_id and header.data_len
    // Note: This assumes the sender and receiver have the same endianness and padding.
}
