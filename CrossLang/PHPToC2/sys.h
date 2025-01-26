#ifndef SYS_H
#define SYS_H

#include <stdint.h>

int install_handler_imp(const char *name);
int sys_call(const char *cmd);
char* validate(const char *name);

#endif // SYS_H
