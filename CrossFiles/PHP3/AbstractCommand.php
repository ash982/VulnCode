<?php

require_once 'CommandInterface.php';

abstract class AbstractCommand implements CommandInterface {
    abstract public function execute(string $command): void;
}
