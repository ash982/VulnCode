<?php

class SystemCommand1 {
    public static function run(string $command): void {
        $output = shell_exec($command);
        if ($output !== null) {
            echo $output;
        } else {
            echo "Command execution failed.\n";
        }
    }
}
?>
