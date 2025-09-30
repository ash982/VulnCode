<?php

// --- 1. SETUP: Define a secret key (MUST be kept secret and secure) ---
$SECRET_KEY = 'your_super_secret_application_key_12345';

// --- 2. GENERATION: Function to Serialize and Sign Data ---

/**
 * Creates a signed, tamper-proof serialized string.
 */
function create_signed_data(array $data, string $key): string {
    // A. Serialize the data
    $serialized_data = serialize($data);

    // B. Create the HMAC signature using a strong algorithm (e.g., sha256)
    $signature = hash_hmac('sha256', $serialized_data, $key);

    // C. Combine the signature and data (e.g., signature.data)
    return $signature . '.' . base64_encode($serialized_data);
}


// --- 3. VERIFICATION: Function to Check Signature and Deserialize ---

/**
 * Verifies the signature and safely deserializes the data.
 */
function verify_and_unserialize(string $signed_string, string $key): mixed {
    // 1. Check for the separator
    if (strpos($signed_string, '.') === false) {
        return false; // Invalid format
    }

    // 2. Split into signature and data parts
    list($provided_signature, $encoded_data) = explode('.', $signed_string, 2);

    // 3. Decode the data
    $serialized_data = base64_decode($encoded_data);

    // 4. Recalculate the expected signature
    $expected_signature = hash_hmac('sha256', $serialized_data, $key);

    // 5. CRITICAL STEP: Compare signatures using a timing-attack safe comparison
    if (!hash_equals($expected_signature, $provided_signature)) {
        // Signature mismatch means data was tampered with! 🚨
        error_log("HMAC Signature Mismatch: Data was modified.");
        return false;
    }

    // 6. Data is verified: Safe to deserialize (optional: limit classes for defense-in-depth)
    return unserialize($serialized_data, ["allowed_classes" => false]); 
}

// --------------------------------------------------------------------------
// --- DEMONSTRATION ---
// --------------------------------------------------------------------------

// --- Scenario 1: Legitimate Data Flow (SUCCESS) ---
$user_session = [
    'user_id' => 101,
    'is_admin' => false,
    'login_time' => time()
];

$signed_payload = create_signed_data($user_session, $SECRET_KEY);
echo "Generated Signed Payload (e.g., for a cookie):\n$signed_payload\n\n";

// Application receives the data and verifies it
$result_legit = verify_and_unserialize($signed_payload, $SECRET_KEY);

echo "✅ Legitimate Deserialization Result:\n";
print_r($result_legit);

// --------------------------------------------------------------------------

// --- Scenario 2: Attacker Tampering (FAILURE) ---
// Attacker attempts to change 'is_admin' from 'false' to 'true' in the base64 part
$tampered_serialized_data = serialize(['user_id' => 101, 'is_admin' => true, 'login_time' => time()]);

// The attacker has the original signature, but the data is different
list($original_signature, $original_encoded_data) = explode('.', $signed_payload, 2);

// Attacker tries to send the original signature with the new, malicious data
$tampered_payload = $original_signature . '.' . base64_encode($tampered_serialized_data);

echo "\n\n❌ Tampered Payload Sent:\n$tampered_payload\n";

// Application receives the tampered data and verifies it
$result_tampered = verify_and_unserialize($tampered_payload, $SECRET_KEY);

echo "Attempted Deserialization Result (Should be false):\n";
var_dump($result_tampered); // Outputs bool(false)
?>
