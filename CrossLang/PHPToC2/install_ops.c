#include "install_ops.h"
#include "sys.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

// Function to validate the name (basic validation example)
char* validate(const char *name) {
    if (name == NULL || strlen(name) == 0) {
        return NULL;
    }

    // Prevent command injection by allowing only alphanumeric and underscores
    for (size_t i = 0; i < strlen(name); i++) {
        if (!(isalnum(name[i]) || name[i] == '_')) {
            return NULL;
        }
    }

    return strdup(name);  // Return a duplicate of the safe name
}

// Function to install the handler
int install_handler_imp(const char *name) {
    if (name == NULL) {
        fprintf(stderr, "Error: Name cannot be NULL.\n");
        return -1;
    }

    char *safe_name = validate(name);
    if (safe_name == NULL) {
        fprintf(stderr, "Error: Invalid name provided.\n");
        return -1;
    }

    char cmd[256];
    snprintf(cmd, sizeof(cmd), "rm -rf %s", safe_name);
    
    int result = sys_call(cmd);  // Call the system command via sys.c
    free(safe_name);  // Free allocated memory

    return result;
}
