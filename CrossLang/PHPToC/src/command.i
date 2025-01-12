// command.i 
%module command
%{
#include "command.h"  // Include the header file
%}
%include "command.h"  // Include the header file for SWIG parsing if the target function already declared in header file
