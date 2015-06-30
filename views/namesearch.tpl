% rebase('base.tpl', title="")

<div class="container">
      
      <form method=GET>
             <input name='name'>
             <input type='submit'> 
      </form>
                
        
        <ul>
        % for link in links:
        <li><a href="{{link['link']}}">{{link['name']}}</a></li>
        % end
        </ul>
</div>