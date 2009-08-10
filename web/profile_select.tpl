#include "web/layout/header.tpl"

<h1>Escolha um perfil</h1>
	
<ul>
#for $profile in $profiles
    <li class="profile">
		<span>$profile.name</span>
		<div style="display:none">
			<form method="GET" action="Account://register">
				<input type="hidden" id="profileName" name="profileName" value="$profile.name"/>
				<p><label for="username">Usu&aacute;rio:</label> <input type="text" id="username" name="username" value="$profile.username"/></p>
				<p><label for="password">Senha:</label> <input type="password" id="password" name="password" value="$profile.password"/></p>
				<p class="submit"><input type="submit" value="Enviar" /></p>
			</form>
		</div>
	</li>
#end for
</ul>

<h2><a href="ProfileManager.new.action">Criar perfil</a></h2>

#include "web/layout/footer.tpl"