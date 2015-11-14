% rebase('base.tpl', title="")

<div class="container">

      <!-- Main component for a primary marketing message or call to action -->
      <div class="jumbotron">
        <h1>Trove Names</h1>
        <p><a href="http://trove.nla.gov.au/">Trove</a> is the National Library of Australia's online digital
        repository.  We've taken the Newspaper holdings from Trove and used Named Entity
        Recognition to find the names of People in the text.  This site provides an interface
        to the results of this process.</p>
        <p>The site provides a query interface in SPARQL and a linked data interface to
        allow you to find out things about people and documents.</p>

   <p>This project is a collaboration between <a href="http://huni.net.au/">HuNI</a>, <a href="http://alveo.edu.au/">Alveo</a> and the National Library of Australia's <a href="http://trove.nla.gov.au/">Trove</a> archive. It was funded by  <a href="http://www.nectar.org.au">NeCTAR</a>.</p>

   <p>
   <form method=GET action='/name'>
          <input name='name' size=30 placeholder="search by first or last name">
          <input type='submit'>
   </form>
   </p>
      </div>




</div> <!-- container-fluid -->


<div class="container deakin-footer-container">
    <div class="col-lg-6 col-md-6 col-sm-12 col-xs-12">
    <p> © Copyright <a href="http://www.mq.edu.au/">Macquarie University</a>. Macquarie University is proud to be in partnership with, and acknowledges funding from,
  the <a href="http://www.nectar.org.au">National eResearch Collaboration Tools and Resources (NeCTAR)</a> project to develop Alveo and HuNI.
  NeCTAR is an Australian Government project conducted as part of the Super Science initiative and financed by the Education Investment Fund.
    </p>

</div>

     <div class="col-lg-2 col-md-2 col-sm-4 col-xs-4 footer-logos">
   <a href="http://alveo.edu.au/"><img src="/static/img/alveo_logo.png" class="img-responsive" title="Alveo Project" alt="Alveo Project" longdesc="http://www.deakin.edu.au/">
   </a>
</div>
     <div class="col-lg-2 col-md-2 col-sm-4 col-xs-4 footer-logos">
   <a href="http://huni.net.au/"><img src="/static/img/huni-logo.png" class="img-responsive" title="HuNI Project" alt="HuNI Project" longdesc="http://www.deakin.edu.au/"></a>
       </div>

       <div class="col-lg-2 col-md-2 col-sm-4 col-xs-4 footer-logos">
         <a href="http://www.nectar.org.au"><img src="http://huni.net.au/images/nectar-logo.png" class="img-responsive" title="National eResearch Collaboration Tools and Resources (NeCTAR)" alt="NeCTAR - National eResearch Collaboration Tools and Resources"></a>
       </div>
</div>
