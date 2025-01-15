import shell_exec

# Take user input
user_input = input("Enter the command to execute: ")

# Pass the input to the C function
shell_exec.execute_command(user_input)

