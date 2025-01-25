<?php

require_once 'InputProcessor.php';

// Simulating tainted input from user
$taintedInput = $_GET['user_input'];

// Create an instance of InputProcessor and process the input
$processor = new InputProcessor($taintedInput);
$processor->process();

?>
