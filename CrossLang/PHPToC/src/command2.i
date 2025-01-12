// command.i
%module command  // Defines the module name
%{
#include "command.h"  // Include the header file
%}

extern void run_shell_command(const char *command);  // Declare the function for SWIG
