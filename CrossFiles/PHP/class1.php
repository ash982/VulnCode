<?php
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
?>
