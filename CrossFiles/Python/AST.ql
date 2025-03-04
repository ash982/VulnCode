import python
import semmle.python.PrintAST

from PrintAstNode ast, Keyword k
where ast.getLocation().getFile().getBaseName() = "class3.py" and k.getArg() = "shell" and k.getValue().toString() = "False"
select k
