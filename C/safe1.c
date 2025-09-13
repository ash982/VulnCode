#include <stdio.h>
#include <string.h>

typedef struct {
    int id;
    double value;
    char code[10];
} SimpleData;

int main() {
    SimpleData source = {101, 3.14, "TEST"};
    SimpleData dest;

    // This is a perfect use case for memcpy.
    // The struct is just a contiguous block of data.
    memcpy(&dest, &source, sizeof(SimpleData));

    printf("Copied ID: %d, Value: %f, Code: %s\n", dest.id, dest.value, dest.code);
    return 0;
}
