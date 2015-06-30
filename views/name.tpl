% rebase('base.tpl', title="")


<div class='container'>
     <h1>{{name}}</h1>
     
     <p><a href="{{associates}}">Find associates</a></p>
     
     <p>Mentiond in these articles:</p>
     <ul>
     % for article in mentioned_in:
       <li><a href="{{article['link']}}">{{article['title']}}</a></li>
     % end
     </ul>
     
</div>