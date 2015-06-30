% rebase('base.tpl', title="")


<div class='container'>
     <h1>{{name}}</h1>
     
     <p><a href="{{associates}}">Find associates</a></p>
     
     <p>Top 50 people mentioned in the same articles as <a href="{{namelink}}">{{name}}</a>:</p>
     <ul>
     % for person in associates:
       <li><a href="{{person['url']}}">{{person['name']}}</a> ({{person['count']}})</li>
     % end
     </ul>
     
</div>