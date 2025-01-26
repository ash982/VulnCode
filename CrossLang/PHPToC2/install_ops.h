#ifndef INSTALL_OPS_H
#define INSTALL_OPS_H

int install_handler_imp(const char *name);
char* validate(const char *name);

OP_HANDLER("install-handler", install_handlder_imp)

#endif // INSTALL_OPS_H
