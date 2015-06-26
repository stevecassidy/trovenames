% rebase('base.tpl', title="Trove Names SPARQL")


  <div id="yasqe"></div>
  <div id="yasr"></div>
  
  <script src='http://cdn.jsdelivr.net/yasr/2.4/yasr.bundled.min.js'></script>
  <script src='http://cdn.jsdelivr.net/yasqe/2.2/yasqe.bundled.min.js'></script>
  <script>
  var yasqe = YASQE(document.getElementById("yasqe"), {
  	sparql: {
  		showQueryButton: true,
          endpoint: '{{endpoint}}'
  	}
  });
  var yasr = YASR(document.getElementById("yasr"), {
  	//this way, the URLs in the results are prettified using the defined prefixes in the query
  	getUsedPrefixes: yasqe.getPrefixesFromQuery
  });

  //link both together
  yasqe.options.sparql.callbacks.complete = yasr.setResponse;
  </script>

