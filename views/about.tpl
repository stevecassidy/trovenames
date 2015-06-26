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
    
&lt;http://trove.stevecassidy.net/name/c428884fffdf3b12412a28f1cafb3acc&gt; a sc:Name ;
        rdf:label &quot;E. Boyd&quot;
   </pre>
  
  
</div>