#include "web/layout/header.tpl"

	<form method="GET" action="Account://register">
		<p><label for="username">Azzu:</label> <input type="text" id="username" name="username"/></p>
		<p><label for="password">Senha:</label> <input type="password" id="password" name="password"/></p>
		<p class="submit"><input type="submit" value="Enviar" /></p>
	</form>

#include "web/layout/footer.tpl"