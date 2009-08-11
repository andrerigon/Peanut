var Call = {}

Call.answer = function(destination){
	go("Account://answer?destination="+destination)
}

Call.hangup = function(destination){
	go("Account://hangup?destination="+destination)
}


var CallListener = {}

CallListener.incomming_call = function(destination){
	showMessage("Ringing: "+ destination)
	byId("btnAnswer").disabled = false;
	
	$("#btnAnswer").click(function(event){
		byId("btnHangup").disabled = false;
		
		$("#btnHangup").click(function(event){
			this.disabled = true;
			Call.hangup(destination)
			showMessage("End call: "+ destination)
		});
		
		this.disabled = true;
		Call.answer(destination)
		showMessage("Ongoing call: "+ destination)
	});

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