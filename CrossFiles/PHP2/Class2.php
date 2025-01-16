<?php

class Class2 {
    private $input;
    private $db;

    public function __construct($input) {
        $this->input = $input;
        $this->db = null;
    }

    public function connectDb($dbName) {
        try {
            $this->db = new PDO("sqlite:$dbName");
            $this->db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
            return true;
        } catch(PDOException $e) {
            echo "Connection failed: " . $e->getMessage();
            return false;
        }
    }

    public function process() {
        echo "Class2 processing: {$this->input}\n";
        if (!$this->db) {
            echo "Database not connected\n";
            return;
        }

        // Potentially unsafe operation
        $query = "SELECT * FROM users WHERE username = '{$this->input}'";
        echo "Executing query: $query\n";

        try {
            $stmt = $this->db->query($query);
            $results = $stmt->fetchAll(PDO::FETCH_ASSOC);
            print_r($results);
        } catch(PDOException $e) {
            echo "Query failed: " . $e->getMessage();
        }
    }

    public function __destruct() {
        $this->db = null;
    }
}
?>
