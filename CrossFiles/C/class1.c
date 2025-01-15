#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "class1.h"

struct Class1 {
    char* input;
};

Class1* class1_create(const char* input) {
    Class1* self = malloc(sizeof(Class1));
    self->input = strdup(input);
    return self;
}

void class1_process(Class1* self) {
    printf("Class1 processing: %s\n", self->input);
    // Potentially unsafe operation
    char command[256];
    snprintf(command, sizeof(command), "echo %s", self->input);
    system(command);
}

void class1_destroy(Class1* self) {
    free(self->input);
    free(self);
}
