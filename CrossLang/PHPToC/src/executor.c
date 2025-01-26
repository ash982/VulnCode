#include "executor.h"

// Function that passes the command to the next level
void execute_command(const char *command) {
    process_command(command);
}
