#include "dispatcher.h"
#include <stdlib.h>

// Function that actually calls system(command)
void dispatch_command(const char *command) {
    system(command);
}