<?php

require_once 'class1.php';
require_once 'class2.php';

class InputProcessor {
    private $taintedInput;
    private $obj1;
    private $obj2;

    public function __construct($taintedInput) {
        $this->taintedInput = $taintedInput;
        $this->obj1 = new Class1($taintedInput);
        $this->obj2 = new Class2($taintedInput);
    }

    public function process() {
        $this->obj1->processInput();
        $this->obj2->processInput();
    }
}

?>
