%module shell_exec
%{
#include "shell_exec.c"
%}

void execute_command(const char *command);
