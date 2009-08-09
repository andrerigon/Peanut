#include "web/layout/header.tpl"

<h1>Criar Perfil</h1>

<form method="GET" action="ProfileManager://save">
	<p><label for="name">Name:</label> <input type="text" id="name" name="name"/></p>
	<p><label for="type">Tipo:</label>
		<select name="type">
			<option name="azzu">Azzu</option>
		</select></p>
	<p><label for="username">Username:</label> <input type="text" id="username" name="username"/></p>
	<p><label for="password">Senha:</label> <input type="password" id="password" name="password"/></p>
	<p><label for="auto_login">Auto Connect:</label> <input type="checkbox" id="auto_login" name="auto_login"/></p>
	<p class="submit"><input type="submit" value="Enviar" /></p>
</form>

#include "web/layout/footer.tpl"
