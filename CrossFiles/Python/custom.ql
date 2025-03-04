/**
 * @kind path-problem
 * @problem.severity error
 * @id py/test1234
 */

 import python
 import semmle.python.dataflow.new.DataFlow
 import semmle.python.dataflow.new.TaintTracking
 import semmle.python.ApiGraphs
 import semmle.python.dataflow.new.RemoteFlowSources
 import MyFlow::PathGraph
 import semmle.python.Concepts


 class ExecuteCall extends DataFlow::CallCfgNode {
    ExecuteCall() {
    this = API::moduleImport("os").getMember("system").getACall() 
    or 
    this = API::moduleImport("subprocess").getMember("Popen").getACall() 

    }
}

 private module MyConfig implements DataFlow::ConfigSig {
   predicate isSource(DataFlow::Node source) {
     source = API::moduleImport("flask").getMember("request").asSource()
     or 
     source = API::moduleImport("sys").getMember("argv").asSource()
   }

   predicate isSink(DataFlow::Node sink) {
     exists(ExecuteCall ec, Keyword k |
         sink = ec.getArg(0) and ec.asExpr().(Call).getArg(_) = k.getAChildNode() and k.getValue().toString() = "True"
         and k.getArg() = "shell"
        )
   }

   predicate isBarrier(DataFlow::Node sanitizer) {
    isShellFalse() //this not working
     and
    sanitizer = API::moduleImport("shlex").getMember("quote").getACall() 
     or 
    sanitizer = API::moduleImport("re").getMember("match").getACall() //this not working in a if clause
    
   }
   additional predicate isShellFalse() {
    exists(Keyword k | k.getArg() = "shell" and k.getValue().toString() = "False") 

   } 

  //  predicate isBarrierIn(DataFlow::Node node) { isSource(node) } 

 } 

 module MyFlow = TaintTracking::Global<MyConfig>; 

 from MyFlow::PathNode source, MyFlow::PathNode sink
 where MyFlow::flowPath(source, sink) 
 select sink.getNode(), source, sink, "execute sink called with untrusted data"
