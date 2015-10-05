% rebase('base.tpl', title="")

<div class="container">

      <p>
   <form method=GET action='/name'>
          <input name='name' size=30 placeholder="search by first or last name">
          <input type='submit'>
   </form>
         </p>

        <ul>
        % for link in links:
        <li><a href="{{link['link']}}">{{link['name']}}</a></li>
        % end
        </ul>
</div>
