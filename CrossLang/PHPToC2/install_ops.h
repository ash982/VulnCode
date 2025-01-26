#ifndef INSTALL_OPS_H
#define INSTALL_OPS_H

// Define a macro to map a handler name to its implementation function
#define OP_HANDLER(handler, handler_imp) \
    static const struct HandlerMapping { \
        const char *name; \
        int (*function)(const char *); \
    } handler##_mapping = { handler, handler_imp };

// Function declarations
int install_handler_imp(const char *name);
char* validate(const char *name);

// Mapping the handler to its implementation
OP_HANDLER("install-handler", install_handler_imp)

#endif // INSTALL_OPS_H
