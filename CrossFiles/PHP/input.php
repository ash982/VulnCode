<?php
// Simulating tainted input from user
$taintedInput = $_GET['user_input'];

// Include other files
require_once 'class1.php';
require_once 'class2.php';

// Create instances and pass tainted input
$obj1 = new Class1($taintedInput);
$obj2 = new Class2($taintedInput);

// Use the classes
$obj1->processInput();
$obj2->processInput();
?>
