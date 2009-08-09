var Call = {}

Call.answer = function(){
	go("Account://answer")
}

Call.hangup = function(){
	go("Account://hangup")
}



var Account = {}

Account.register = function(profileName){
	go("Account://register?profileName="+profileName)
}

Account.logout = function(){
	go("Account://unregister")
}

Account.balance = function(){
	go("Account://balance")
}