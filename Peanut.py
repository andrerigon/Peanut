import pjsua as pj
import socket
import hashlib
import re

def log_cb(level, str, len):
	"Loggin callback"
	print str


class Phone():

	def __init__( self ):
		"Phone init method"

	def start( self ):
		"Phone Startup"
		lib = pj.Lib()
		lib.init( log_cfg = pj.LogConfig( level=3, callback=log_cb ) )
		transport = lib.create_transport( pj.TransportType.UDP )
		lib.start()
		
		self.accounts = {}
		
		return self

	def stop( self ):
		"Phone Shutdown"
		self.accounts = None
		
		lib = pj.Lib.instance() 
		if lib == None:
			return
		lib.hangup_all()
		lib.destroy()
		lib = None
		return self

	def register( self, username, password, accountType = 'azzu', accountListener = None, callListener = None ):
		"Make an account register"
		if accountListener == None:
			accountListener = AccountListener()
		if callListener == None:
			callListener = CallListener()
			
		accountKey = GenericAccount.accountKey( username, accountType )
			
		# TODO do this with spring 
		delegateAccount = AzzuAccount( username, password )
		account = GenericAccount( accountKey, accountListener, callListener, delegateAccount )
		
		self.accounts[ accountKey ] = account
		
		account.register()
		
		return account
	
	def unregister( self, username, accountType = 'azzu' ):
		accountKey = GenericAccount.accountKey( username, accountType )
		self.accounts.pop( accountKey ).unregister()
	
	def getAccount( self, username, accountType = 'azzu' ):
		accountKey = GenericAccount.accountKey( username, accountType )
		return self.accounts[ accountKey ]


class GenericAccount():

	def __init__( self, key, listener, callListener, delegate ):
		"Init of GenericAccount"
		self.key = key
		self.listener = listener
		self.callListener = callListener
		self.registered = False
		self.delegate = delegate
		self.calls = {}
		
	def register( self ):
		"Register this account"
		self.listener.onRegisterRequest( self )
		self.delegate = self.delegate.register( self )
		return self

	def registerSuccess( self ):
		"Invoked when this account registred successfully"
		self.registered = True
		self.listener.onRegisterSuccess( self )

	def registerError( self ):
		self.registered = False
		"Invoked when this account has an error during its register"
		self.listener.onRegisterError( self )

	def unregister( self ):
		self.delegate.unregister()
		self.registered = False
		self.listener.onUnregister( self )

	def call( self, destination ):
		peanutCall = self.delegate.call( destination, self )
		self.calls[ str( peanutCall.destination() ) ] = peanutCall
		return peanutCall

	def incomingCall( self, call ):
		"Register incoming call to the account"
		peanutCall = Call( call )
		
		# Register call
		self.calls[ str( peanutCall.destination() ) ] = peanutCall
		
		# Create Call Callback
		callCallback = CallCallback( self, peanutCall )
		call.set_callback( callCallback )
		
		# Answer with a ring
		peanutCall.ring()
		
		# Trigger incoming call event
		self.listener.onIncomingCall( self, peanutCall )
		
	def answerCall( self, destination ):
		self.calls[ str( destination ) ].answer()
		
	def hangupCall( self, destination ):
		self.calls[ str( destination ) ].hangup()
		
	def unregisterCall( self, peanutCall ):
		self.calls.pop( peanutCall.destination() )

	@staticmethod
	def accountKey( username, accountType ):
		stringKey = str( username ) + str( accountType )
		return hashlib.md5( stringKey ).hexdigest()


class AzzuAccount():

	def __init__( self, username, password ):
		"Init of a Azzu Account"
		self.username = str( username )
		self.password = str( password )

	def register( self, genericAccount ):
		"Create a Azzu Account"
		lib = pj.Lib.instance()
		self.proxy = socket.gethostbyname( 'proxy.azzu.com.br' )
		accountConfig = pj.AccountConfig( self.proxy, self.username, self.password )
		self.account = lib.create_account( accountConfig, cb = AccountCallback( genericAccount ) )
		return self

	def unregister( self ):
		"Unregister this account"
		self.account.delete()

	def call( self, destination, genericAccount ):
		"Make a call for the destination"
		callString = 'sip:' + str( destination ) + '@' + self.proxy
		callCallback = CallCallback( genericAccount )
		call = self.account.make_call( callString, callCallback )
		return Call( call )


class AccountListener():

	def __init__( self ):
		"Init an Account Listener"

	def onRegisterRequest( self, account ):
		"Invoked when the account register is requested"
		print 'Account Register requested: username ' + account.delegate.username

	def onRegisterSuccess( self, account ):
		"Invoked when the account registred successfully"
		print 'Account Registred: username ' + account.delegate.username

	def onRegisterError( self, account ):
		"Invoked when the account has a regiter error"
		print 'Error Registering the Account: username ' + account.delegate.username

	def onUnregister( self, account ):
		"Invoked when the account was unregistered"
		print 'Account Unregistered: username ' + account.delegate.username

	def onIncomingCall( self, account, peanutCall ):
		"Invoked when the account receive an incoming call"
		print 'Incoming Call for account with username ' + account.delegate.username + ' from: ' + peanutCall.destination()


class AccountCallback( pj.AccountCallback ):

	def __init__( self, peanutAccount, account=None, ):
		"Create an Account Callback for the passed account"
		self.peanutAccount = peanutAccount
		pj.AccountCallback.__init__( self, account )

	def on_incoming_call( self, call ):
		# Register the incomming call into the account 
		self.peanutAccount.incomingCall( call )

	def on_reg_state( self ):
		"Register handler"
		print 'reg_status: ' + str( self.account.info().reg_status ) + ' reason: ' + self.account.info().reg_reason
		if self.account.info().reg_status == 200:
			self.peanutAccount.registerSuccess()
		if self.account.info().reg_status > 700:
			self.peanutAccount.registerError()


class Call():

	def __init__( self, call ):
		"Create a Call receiving a pjsua call"
		self.call = call
		self.speakOnConf = False
		
	def destination( self ):
		regex = re.match('<?sip:(\d+)@', str(self.call.info().remote_uri))
		return regex.group(1)

	def answer( self ):
		"Answer the call"
		self.call.answer()
		return self

	def ring( self ):
		"Return ring status"
		if self.call.info().state == pj.CallState.INCOMING:
			self.call.answer( code = 180 )
		return self

	def hangup( self ):
		"Hangup a call from the phone"
		self.call.hangup()
		return self

	def dtmf( self, digits ):
		"Send DTMF digits"
		self.call.dial_dtmf( digits )
		return self

	def hold( self ):
		"Put this call on hold"
		self.call.hold()
		return self

	def unhold( self ):
		"Unhold this call"
		self.call.unhold()
		return self

	def mute( self ):
		"Mute this call"
		AudioManager().disconnectOutputAudio( self.call )
		return self

	def unmute( self ):
		AudioManager().connectOutputAudio( self.call )
		return self
	

class CallListener():

	def __init__( self ):
		"Init a Call Listener"

	def onCalling( self, peanutAccount, peanutCall ):
		"Invoked when a call is started but is not connected or finished"
		print 'Trying to call to ' + peanutCall.destination()

	def onRinging( self, peanutAccount, peanutCall ):
		"Invoked when a call is in ringing status"
		print 'Ringing call with ' + peanutCall.destination()

	def onConnecting( self, peanutAccount, peanutCall ):
		"Invoked when a call is connecting"
		print 'Connecting call with ' + peanutCall.destination()

	def onAnswer( self, peanutAccount, peanutCall ):
		"Invoked when a call is answered"
		print 'Call answered with ' + peanutCall.destination()

	def onFinished( self, peanutAccount, peanutCall ):
		"Invoked when a call is finished"
		peanutAccount.unregisterCall( peanutCall )
		print 'Call finished with ' + peanutCall.destination()
# TODO add more usefull listener methods


class CallCallback( pj.CallCallback ):

	def __init__( self, peanutAccount, peanutCall=None, call=None ):
		"Create a Call Callback"
		self.callListener = peanutAccount.callListener
		self.peanutAccount = peanutAccount
		self.peanutCall = peanutCall
		pj.CallCallback.__init__( self, call )

	def on_state( self ):
		"Intercept any call state change"
		if self.peanutCall == None:
			self.peanutCall = Call( self.call )
		# State where an outcoming call has just been requested
		if self.call.info().state == pj.CallState.CALLING:
			self.callListener.onCalling( self.peanutAccount, self.peanutCall )
		# State where a call is in ringing
		elif self.call.info().state == pj.CallState.EARLY:
			self.callListener.onRinging( self.peanutAccount, self.peanutCall )
		# State where a call was received and is almost confirmed
		elif self.call.info().state == pj.CallState.CONNECTING:
			self.callListener.onConnecting( self.peanutAccount, self.peanutCall )
		# State where a call is answered and confiremd
		elif self.call.info().state == pj.CallState.CONFIRMED:
			self.callListener.onAnswer( self.peanutAccount, self.peanutCall )
		# State where a call is finished and disconnected
		elif self.call.info().state == pj.CallState.DISCONNECTED:
			self.callListener.onFinished( self.peanutAccount, self.peanutCall )

	def on_media_state( self ):
		"Intercept any media state change"
		if self.call.info().media_state == pj.MediaState.ACTIVE:
			AudioManager().connectCallAudio( self.call )


class AudioManager():

	def __init__( self ):
		"Init method for AudioManager"

	def connectConfAudio( self, calls ):
		"Connect the slots to make a conference"
		lib = pj.Lib.instance()
		for c1 in calls:
			if c1.speakOnConf:
				for c2 in calls:
					if c1 != c2:
						slot1 = c1.call.info().conf_slot
						slot2 = c2.call.info().conf_slot
						lib.conf_connect( slot1, slot2 )

	def connectCallAudio( self, call ):
		"Connect the call slot to the audio device"
		lib = pj.Lib.instance()
		callSlot = call.info().conf_slot
		lib.conf_connect( callSlot, 0 )
		lib.conf_connect( 0, callSlot )

	def disconnectCallAudio( self, call ):
		"Disconnect the call slot to the audio device"
		lib = pj.Lib.instance()
		callSlot = call.info().conf_slot
		lib.conf_disconnect( callSlot, 0 )
		lib.conf_disconnect( 0, callSlot )

	def connectOutputAudio( self, call ):
		"Connect only de output slot to the call slot"
		lib = pj.Lib.instance()
		callSlot = call.info().conf_slot
		lib.conf_connect( 0, callSlot )

	def disconnectOutputAudio( self, call ):
		"Disconnect only de output slot to the call slot"
		lib = pj.Lib.instance()
		callSlot = call.info().conf_slot
		lib.conf_disconnect( 0, callSlot )

	def listAudioDevices( self ):
		"List all the audio devices into the system"
		lib = pj.Lib.instance()
		devices = lib.enum_snd_dev()
		peanutDevices = []
		i = 0
		for dev in devices:
			peanutDevices.append( AudioDevice( dev, i ) )
			i += 1
		return peanutDevices

	def setAudioDevices( self, input, output ):
		"Set the input and the output device for the PeanutPhone"
		lib = pj.Lib.instance()
		lib.set_snd_dev( input.id, output.id )

		
class AudioDevice():

	def __init__( self, device, id ):
		"Initialize a Peanut AudioDevice wrapper class"
		self.device = device
		self.id = id

	def isOutput( self ):
		"Returns true if this is an output device"
		return self.device.output_channels > 0

	def isInput( self ):
		"Return true if this is an input device"
		return self.device.input_channels > 0

	def deviceType( self ):
		"Return a string that describes the type of the device"
		if self.isOutput():
			return 'OUTPUT'
		elif self.isInput():
			return 'INPUT'
		return 'NULL'
			
	def isActive( self ):
		"Return true if this device is currently used by the phone"
		lib = pj.Lib.instance()
		activeIds = lib.get_snd_dev()
		if self.isInput():
			return self.id == activeIds[0]
		elif self.isOutput():
			return self.id == activeIds[1]
		return False

	def name( self ):
		"Returns the name of the device"
		return self.device.name

	def __str__( self ):
		return 'Device { id:' + str( self.id ) + ', name:' + self.name() + \
		', active: ' + str( self.isActive() ) + ', type:' + self.deviceType() + '}'
		
