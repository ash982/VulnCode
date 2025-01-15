#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "class1.h"
#include "class2.h"

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: %s <input>\n", argv[0]);
        return 1;
    }

    char *tainted_input = argv[1];

    Class1 *obj1 = class1_create(tainted_input);
    Class2 *obj2 = class2_create(tainted_input);

    class1_process(obj1);

    // Connect to the database before processing
    if (class2_connect_db(obj2, "example.db")) {
        class2_process(obj2);
    } else {
        printf("Failed to connect to the database.\n");
    }

    class1_destroy(obj1);
    class2_destroy(obj2);

    return 0;
}


