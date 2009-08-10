#include "web/layout/header.tpl"

<form method="GET" action="Account://call">
	<p><label for="destination">Numero:</label> <input type="text" id="destination" name="destination"/></p>
	<p><input type="submit" value="Discar" />
		<input type="button" value="Desligar" onclick="Call.hangup()" />
		<input type="button" value="Atender" onclick="Call.answer()" /></p>
</form>
<center>
<a href="javascript: Account.balance()">Saldo</a> |  
<a href="javascript: Account.logout()">Logout</a>
</center>

#include "web/layout/footer.tpl"
