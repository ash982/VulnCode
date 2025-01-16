<?php

class Class1 {
    private $input;

    public function __construct($input) {
        $this->input = $input;
    }

    public function process() {
        echo "Class1 processing: {$this->input}\n";
        // Potentially unsafe operation
        system("echo " . $this->input);
    }
}
?>
