function go(url){
	window.location.href = url;
}

function byId(elementName){
	return 	document.getElementById(elementName);
}

function showMessage(message){
	byId('msg').innerHTML = message; 
}