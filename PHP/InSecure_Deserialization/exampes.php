<?php
// --- Taint Sources (User Input) ---
$get_data = $_GET['data'];
$post_data = $_POST['config'];
$cookie_data = $_COOKIE['session'];
$request_data = $_REQUEST['settings'];

// --- Vulnerable Cases (True Positives: Tainted Data to Sink) ---

$object_g = unserialize($get_data);

$object_p = unserialize($post_data);

$object_c = unserialize($cookie_data);

$object_r = unserialize($request_data);

// Tainted data passed through an intermediate variable
$t_data = $get_data;
$object_t = unserialize($t_data);


// --- Secure Cases (True Negatives) ---

// 1. Deserializing Hardcoded (Trusted) Data
$trusted_data = 'O:4:"User":1:{s:8:"username";s:5:"admin";}';
$object_trusted = unserialize($trusted_data);

// 2. Deserializing Data Read from a Verified File (Assuming the file read itself is secure)
$file_data = file_get_contents('/tmp/safe_data.txt');
$object_file = unserialize($file_data);

// 3. Using JSON instead of native PHP serialization
// JSON is generally a safer alternative as it only handles primitive types
// and does not trigger magic methods or object instantiation on its own.
$json_data = json_decode($get_data);
$object_safe = $json_data;

// 4. Using the `allowed_classes=false` mitigation (for PHP 7.0+) --- not 100% secure
// This option prevents all object instantiation, turning it into a data-only process.
// The Semgrep rule should not flag this if the rule included logic for the optional argument,
// but since the original rule is simplified for broad detection, we mark it as OK for testing.
$safely_deserialized = unserialize($get_data, ["allowed_classes" => false]);
?>




