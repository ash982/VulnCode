<?php
// Simulating tainted input from user
$taintedInput = $_GET['user_input'];


class Class1 {
    private $input;

    public function __construct($input) {
        $this->input = $input;
    }

    public function processInput() {
        echo "Class1 processing: " . $this->input . "\n";
        // Potentially unsafe operation
        eval("echo 'Evaluated in Class1: " . $this->input . "';");
    }
}

// Create instances and pass tainted input
$obj1 = new Class1($taintedInput);

// Use the classes
$obj1->processInput();
?>
