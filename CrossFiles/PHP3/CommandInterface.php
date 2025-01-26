<?php

interface CommandInterface {
    public function execute(string $command): void;
}
?>
