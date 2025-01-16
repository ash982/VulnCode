<?php

require_once 'Class1.php';
require_once 'Class2.php';

if ($argc < 2) {
    echo "Usage: php {$argv[0]} <input>\n";
    exit(1);
}

$taintedInput = $argv[1];

$obj1 = new Class1($taintedInput);
$obj2 = new Class2($taintedInput);

$obj1->process();
$obj2->process();
?>
