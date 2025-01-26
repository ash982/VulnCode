<?php

require_once 'AbstractCommand.php';

class ShellCommand extends AbstractCommand {
    /**
      * @external
      */
    public function execute(string $command): void {
        $this->runShellCommand($command);
    }

    protected function runShellCommand(string $command): void {
        SystemCommand::run($command);
    }
}
