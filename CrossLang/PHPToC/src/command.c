// command.c
#include "command.h"
#include <stdlib.h>

// Function to execute a shell command
void run_shell_command222(const char *command) {
    system(command);
}

