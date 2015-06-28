% rebase('base.tpl', title="Trove Names")

<div class="container-fluid">
    <p>
        The Trove Names dataset has been extracted from the 
        <a href="http://trove.nla.gov.au/newspaper">National
        Library Trove Newspaper Collection</a> using the 
        <a href="http://nlp.stanford.edu/software/CRF-NER.shtml">Stanford 
        Named Entity</a> tagger.  The results have been turned into
        an RDF dataset and this is presented here with a 
        <a href="http://www.w3.org/TR/rdf-sparql-query/">SPARQL</a> endpoint
        to allow open queries.
    </p>
    
    <p>
        The structure of the RDF data is as illustrated by this 
        example.  There are three kinds of entity: Collection, 
        Work and Name.  
    </p>
    
    <pre class='code'>
@prefix schema: &lt;http://schema.org/&gt; .
@prefix dcterms: &lt;http://purl.org/dc/terms/&gt; .
@prefix tr: &lt;http://trove.stevecassidy.net/schema/&gt; .

&lt;http://trove.stevecassidy.net/source/48f6773c6d425d3011d9a387de1c02d0&gt; a dcterms:Collection ;
    dcterms:title "Seymour Express and Goulburn Valley, Avenel, Graytown, Nagambie, Tallarook and Yea Advertiser (Vic. : 1882 - 1891; 1914 - 1918)"
    dcterms:hasPart &lt;http://trove.nla.gov.au/ndp/del/article/164419550&gt;,
                &lt;http://trove.nla.gov.au/ndp/del/article/164419553&gt;,
                &lt;http://trove.nla.gov.au/ndp/del/article/92151619&gt;.
                
&lt;http://trove.nla.gov.au/ndp/del/article/92151619&gt; a cc:Work ;
    dcterms:created &quot;1917-09-28&quot; ;
    dcterms:source &lt;http://trove.stevecassidy.net/source/48f6773c6d425d3011d9a387de1c02d0&gt; ;
    dcterms:title &quot;RAILWAY SOCIAL&quot; ;
    schema:mentions &lt;http://trove.stevecassidy.net/name/c428884fffdf3b12412a28f1cafb3acc&gt; .
    
&lt;http://trove.stevecassidy.net/name/c428884fffdf3b12412a28f1cafb3acc&gt; a tr:Name ;
        rdf:label &quot;E. Boyd&quot;
   </pre>
  
  <p>The website also provides information about names found in the texts via HTTP requests
          to the following URLs:</p>
          
   <ul>
           <li><code>http://trove.stevecassidy.net/name/&lt;nameid&gt;</code>
           returns a JSON result with the name associated with this node and
           a list of the articles that this name is found in.</li>
                   
                   
           <li><code>http://trove.stevecassidy.net/source/&lt;sourceid&gt;</code>
            returns a JSON result with a list of the article URLs that are 
            contained in this source and the title of the source.</li>
            
            <li><code>http://trove.stevecassidy.net/associates/&lt;nameid&gt;</code>
           returns a JSON result with a list of the <em>associates</em> of this
           name id. An associate is any name that is referenced in one or more
           articles with the other name.  An optional <code>limit</code> query
           variable can be added to restrict the number of results.</li>         
    </ul>
  
  
  
  
</div>