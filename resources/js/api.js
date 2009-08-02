var Call = {}

Call.answer = function(){
	go("Account://answer")
}

Call.hungup = function(){
	go("Account://hungup")
}



var Account = {}

Account.logout = function(){
	go("Account://unregister")
}

Account.balance = function(){
	go("Account://balance")
}