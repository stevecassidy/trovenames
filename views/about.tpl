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
        Work and Name.  A Collection corresponds to a newspaper title and links to all 
        of the individual articles.  Each article has a title and date and we've also added
        a year property to make time based queries easier.  An article has a <code>schema:mentions</code>
        link to a Name instance - note that this is a name and not a person since there 
        will be many people sharing any given name.  The Name record has a label property
        which is the name string but we've also split out the individual words in the name
        in lowercase and the lastname in lowercase as separate properties to help searching.
    </p>
    
    <pre class='code'>
@prefix cc: &lt;https://creativecommons.org/ns#&gt; .
@prefix dcterms: &lt;http://purl.org/dc/terms/&gt; .
@prefix rdf: &lt;http://www.w3.org/1999/02/22-rdf-syntax-ns#&gt; .
@prefix rdfs: &lt;http://www.w3.org/2000/01/rdf-schema#&gt; .
@prefix schema: &lt;http://schema.org/&gt; .
@prefix trovenamesq: &lt;http://trove.stevecassidy.net/schema/&gt; .
@prefix xml: &lt;http://www.w3.org/XML/1998/namespace&gt; .
@prefix xsd: &lt;http://www.w3.org/2001/XMLSchema#&gt; .

&lt;http://trove.stevecassidy.net/source/62aebcd1a45594ab33295a5c2a63f103&gt; a dcterms:Collection ;
    dcterms:hasPart &lt;http://trove.nla.gov.au/ndp/del/article/10000009&gt;,
        &lt;http://trove.nla.gov.au/ndp/del/article/10000017&gt;,
        &lt;http://trove.nla.gov.au/ndp/del/article/10000023&gt;;
    dcterms:title &quot;The Mercury (Hobart, Tas. : 1860 - 1954)&quot; .

&lt;http://trove.nla.gov.au/ndp/del/article/10000009&gt; a cc:Work ;
    dcterms:created &quot;1909-11-19&quot; ;
    dcterms:source &lt;http://trove.stevecassidy.net/source/62aebcd1a45594ab33295a5c2a63f103&gt; ;
    dcterms:title &quot;SPORTING. THE TURF. HOBART TROTTING CLUB.&quot; ;
    schema:mentions &lt;http://trove.stevecassidy.net/name/0d680f66a21d8099c168271eadc084c2&gt; ;
    trovenamesq:context &quot;... the list, claims St winners. Stanley Wootton, Frank&#x27;s younger brotheir, ha...&quot; ;
    trovenamesq:year 1909 .

&lt;http://trove.stevecassidy.net/name/0d680f66a21d8099c168271eadc084c2&gt; a trovenamesq:Name ;
    trovenamesq:lastname &quot;wootton&quot; ;
    trovenamesq:word &quot;stanley&quot;, &quot;wootton&quot; ;
    rdf:label &quot;Stanley Wootton&quot; .

   </pre>
  
  <p>The website provides a JSON api for this data alongside the HTML pages. A request
  with an Accept header containing <code>application/json</code> will get a
  JSON response as follows:</p>
          
   <ul>
           <li><code>http://trove.stevecassidy.net/name/&lt;nameid&gt;</code>
           returns a JSON result with the name associated with this node and
           a list of the articles that this name is found in (currently limited
           to the first 100 articles).</li>
            
            <li><code>http://trove.stevecassidy.net/associates/&lt;nameid&gt;</code>
           returns a JSON result with a list of the <em>associates</em> of this
           name id. An associate is any name that is referenced in one or more
           articles with the other name.  An optional <code>limit</code> query
           variable can be added to restrict the number of results, by default
           50 associates are shown.</li>         
                   
           <li><code>http://trove.stevecassidy.net/source/&lt;sourceid&gt;</code>
            returns a JSON result with a list of the article URLs that are 
            contained in this source and the title of the source.</li>

    </ul>
  
  
  
  
</div>