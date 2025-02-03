#include "sys.h"
#include <stdlib.h>

int sys_call(const char *cmd) {
    if (cmd == NULL) {
        return -1;  // Error: null command
    }

    int ret = system(cmd);
    return WIFEXITED(ret) ? WEXITSTATUS(ret) : -1;
}
