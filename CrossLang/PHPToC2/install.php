<?php 
    /**
      * @external
      */
    public function install(string $name) {
      $req = $name;
      return Direct::runCom($req)
    }

?>
