<?php
require_once 'DatabaseConnection.php';

class Class2 {
    private $input;
    private $db;

    public function __construct($input) {
        $this->input = $input;
        $this->db = new DatabaseConnection();
    }

    public function processInput() {
        echo "Class2 processing: " . $this->input . "\n";
        
        $connection = $this->db->connect();
        if ($connection) {
            // Use prepared statements to prevent SQL injection
            $query = "SELECT * FROM users WHERE username = ?";
            $results = $this->db->fetchAll($query, [$this->input]);
            
            echo "Query results:\n";
            print_r($results);

            $this->db->close();
        }
    }
}
?>
