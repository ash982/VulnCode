#include "sys.h"
#include <stdlib.h>

// Function to execute a system command safely
int sys_call(const char *cmd) {
    if (cmd == NULL) {
        return -1;  // Error: null command
    }

    int ret = system(cmd);
    return WIFEXITED(ret) ? WEXITSTATUS(ret) : -1;
}
