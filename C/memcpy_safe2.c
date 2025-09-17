#include <string.h>
#include <stdlib.h>

void process_data(const int* data, size_t size) {
    // Make a local, modifiable copy of the data.
    int* local_copy = malloc(size * sizeof(int));
    if (!local_copy) { /* handle allocation failure */ return; }

    memcpy(local_copy, data, size * sizeof(int));
    
    // ... work with local_copy ...

    free(local_copy);
}
