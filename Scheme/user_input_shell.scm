(import (chicken process)
        (chicken io))

(define (run-shell-command input)
  (let ((result (process-output (string-append "echo " input))))
    (print "Shell command output: " result)))

(display "Enter a string to pass to the shell command: ")
(flush-output)
(let ((user-input (read-line)))
  (run-shell-command user-input))
