<?php

require_once 'ShellCommand.php';

$commandExecutor = new ShellCommand();
$commandExecutor->execute('ls -l');
?>
