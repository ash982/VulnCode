<?php
require_once 'classes/Validator.php';
require_once 'classes/Enricher.php';

$result = null;
$error = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    try {
        // Validate user input
        //$validatedInput = Validator::validateInput($_POST['user_input']);
        $taintedInput = Validator::validateInput($_POST['user_input']);

        // Enrich user input with additional data
        //$result = Enricher::enrichInput($validatedInput);
        $result = Enricher::enrichInput($taintedInput);

    } catch (Exception $e) {
        $error = $e->getMessage();
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Home</title>
</head>
<body>
    <h1>User Input Application</h1>
    <form method="POST" action="home.php">
        <label for="user_input">Enter your input:</label>
        <input type="text" id="user_input" name="user_input" required>
        <button type="submit">Submit</button>
    </form>

    <?php if ($error): ?>
        <div style="color: red;">
            <strong>Error:</strong> <?= htmlspecialchars($error, ENT_QUOTES, 'UTF-8') ?>
        </div>
    <?php endif; ?>

    <?php if ($result): ?>
        <div style="margin-top: 20px;">
            <h2>Result</h2>
            <!-- <p><strong>Input:</strong> <?= htmlspecialchars($result['user_input'], ENT_QUOTES, 'UTF-8') ?></p> -- >
            <p><strong>Input:</strong> <?= $result['user_input'] ?></p>
            <p><strong>IP Address:</strong> <?= htmlspecialchars($result['ip'], ENT_QUOTES, 'UTF-8') ?></p>
            <p><strong>Timestamp:</strong> <?= htmlspecialchars($result['timestamp'], ENT_QUOTES, 'UTF-8') ?></p>
        </div>
    <?php endif; ?>
</body>
</html>
