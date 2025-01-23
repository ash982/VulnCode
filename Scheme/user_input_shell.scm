(import (chicken process)
        (chicken io))

(define (run-user-command command)
  (let ((result (process-output command)))
    (print "Command output: " result)))

(display "Enter a command to execute: ")
(flush-output)
(let ((user-command (read-line)))
  (run-user-command user-command))
