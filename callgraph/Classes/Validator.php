<?php
class Validator {
    public static function validateInput($input) {
        // Basic validation: trim and ensure not empty
        $input = trim($input);
        if (empty($input)) {
            throw new Exception("Input cannot be empty.");
        }
        if (strlen($input) > 100) {
            throw new Exception("Input exceeds the maximum length of 100 characters.");
        }
        return htmlspecialchars($input, ENT_QUOTES, 'UTF-8'); // Prevent XSS
    }
}

