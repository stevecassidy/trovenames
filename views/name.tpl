% rebase('base.tpl', title="Matches for name")


<div class='container'>
     <h1>{{name}}</h1>

     <p><a href="{{associates}}">Find associates</a></p>

     <p>Mentiond in these articles:</p>

     <div class='pager'>
     % if next > 1:
     <a href="?page={{page-1}}">&lt;&lt;Previous Page</a>
     % end
     % if len(mentioned_in) == 100:
     <a href="?page={{page+1}}">Next Page &gt;&gt;</a>
     % end
     </div>

     <ul>
     % for article in mentioned_in:
       <li>{{article['date']}} <a href="{{article['link']}}">{{article['title']}}</a> (<a href="{{article['textlink']}}">text</a>)</li>
     % end
     </ul>

     <div class='pager'>
     % if next > 1:
     <a href="?page={{page-1}}">&lt;&lt;Previous Page</a>
     % end
     % if len(mentioned_in) == 100:
     <a href="?page={{page+1}}">Next Page &gt;&gt;</a>
     % end
     </div>
</div>
