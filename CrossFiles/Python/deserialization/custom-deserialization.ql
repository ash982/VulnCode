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
    this = API::moduleImport("pickle").getMember("load").getACall()  //pickle.load(ds) 
    or 
    this = API::moduleImport("pickle").getMember("loads").getACall()  //pickle.loads(data)
    or 
    this = API::moduleImport("shelve").getMember("open").getACall()  //shelve.open(data)

    }
}

 private module MyConfig implements DataFlow::ConfigSig {
   predicate isSource(DataFlow::Node source) {
     source = API::moduleImport("flask").getMember("request").asSource()
     or 
    //  source = API::moduleImport("socket").getMember("socket").getMember("recvfrom").asSource() //this is not working
    //  source = API::moduleImport("socket").getMember("socket").asSource()  //return "socket.socket"
    //  source = API::moduleImport("socket").getMember("socket").getASuccessor().asSource() //return "socket.socket(socket.AF_INET, socket.SOCK_DGRAM)"
    //  source = API::moduleImport("socket").getMember("socket").getASuccessor().getASuccessor().asSource() //return "s.bind", "s.recvfrom", "s.sendto"
     source = API::moduleImport("socket").getMember("socket").getASuccessor().getASuccessor().getACall() //use AST tree, the default source does not include socket, how to modle it in yaml?

   }

   predicate isSink(DataFlow::Node sink) {
    //  exists(DataFlow::Node n | sink = n)

     exists(ExecuteCall ec |
        sink = ec.getArg(0)   //ds, data
     )    
   }
} 

 module MyFlow = TaintTracking::Global<MyConfig>; 

 from MyFlow::PathNode source, MyFlow::PathNode sink
 where MyFlow::flowPath(source, sink) 
 select sink.getNode(), source, sink, "execute sink called with untrusted data"
