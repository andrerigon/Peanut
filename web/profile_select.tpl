#include "web/layout/header.tpl"

<h1>Escolha um perfil</h1>

<ul>
#for $profile in $profiles
    <li><a href="javascript: Account.register('$profile.name')">$profile.name</a></li>
#end for
</ul>

<h2><a href="ProfileManager.new.action">Criar perfil</a></h2>

#include "web/layout/footer.tpl"