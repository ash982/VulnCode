// command.c
#include "command.h"
#include <stdlib.h>

// Function to execute a shell command
void run_shell_command(const char *command) {
    system(command);
}

