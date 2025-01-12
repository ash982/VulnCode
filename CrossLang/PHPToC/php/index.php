<?php
// Include the SWIG-generated PHP wrapper
dl("command.so");

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $command = $_POST['command'];

    // Sanitize the user input (Important for security)
    $safe_command = escapeshellcmd($command);

    // Call the C function
    run_shell_command($safe_command);

    echo "Command executed: $safe_command";
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PHP to C Command Executor</title>
</head>
<body>
    <h2>Execute a Command</h2>
    <form method="POST">
        <label for="command">Enter Command:</label>
        <input type="text" id="command" name="command" required>
        <button type="submit">Run</button>
    </form>
</body>
</html>
