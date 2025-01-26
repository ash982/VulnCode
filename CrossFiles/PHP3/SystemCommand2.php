<?php

class SystemCommand2 {
    public static function run(string $command): void {
        $output = [];
        $returnVar = 0;
        exec($command, $output, $returnVar);

        if ($returnVar === 0) {
            echo implode("\n", $output) . "\n";
        } else {
            echo "Command execution failed with code: $returnVar\n";
        }
    }
}
?>
