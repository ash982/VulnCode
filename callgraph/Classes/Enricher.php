<?php
class Enricher {
    public static function enrichInput($input) {
        // Add user IP and timestamp
        $ip = $_SERVER['REMOTE_ADDR'];
        $timestamp = date('Y-m-d H:i:s');
        return [
            'input' => $input,
            'ip' => $ip,
            'timestamp' => $timestamp
        ];
    }
}
