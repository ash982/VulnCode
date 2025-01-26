<?php

class SystemCommand {
    public static function run(string $command): void {
        system($command);
    }
}
?>
