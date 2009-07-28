import pjsua as pj
import socket

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
        return self
    def stop( self ):
        "Phone Shutdown"
        lib = pj.Lib.instance() 
        if lib == None:
            return
        lib.hangup_all()
        lib.destroy()
        lib = None
        return self
    def register( self, username, password ):
        "Make an account register"
	# TODO The Listener's should be passed by parameters
        account = GenericAccount( username, password, AccountListener(), CallListener() )
        account.register()
        return account

class GenericAccount():
    def __init__( self, username, password, listener, call_listener ):
        "Init of GenericAccount"
        self.incoming_calls = {} 
        self.id_call = 0
        self.listener = listener
        self.call_listener = call_listener
        # TODO add strategy logic for accounts 
        self.delegate = AzzuAccount( username, password, self )
    def next_id_call( self ):
        self.id_call += 1
        return self.id_call
    def register( self ):
        self.delegate = self.delegate.register()
        return self
    def unregister( self ):
        self.delegate.unregister()
    def call( self, destination ):
        return self.delegate.call( destination, self.next_id_call() )
    def incoming_call( self, call ):
        "Register incoming call to the account"
        # Create Peanut Call
        id_call = self.next_id_call()
        peanut_call = Call( call, id_call )
        # Create Call Callback
        call_callback = CallCallback( self.call_listener, peanut_call, call )
        call.set_callback( call_callback )
        # Append an incoming call to the phone
        self.incoming_calls[ id_call ] = peanut_call
        # Answer with a ring
        peanut_call.ring()
    def answer( self, id_call = 0 ):
	"Answer the call from the provided callId"
        call = self.pop_incoming_call( id_call )
        call.answer()
        return call
    def hangup_incoming_call( self, id_call = 0 ):
        "Hangup the call from the provided callId"
        call = self.pop_incoming_call( id_call )
        call.hangup()
    def pop_incoming_call( self, id_call = 0 ):
        "Pop the incomming call for the passed id"
        if id_call == 0:
            call = self.incoming_calls.values()[0]
            del self.incoming_calls[ self.incoming_calls.keys()[0] ]
        else:
            call = self.incoming_calls[ id_call ]
            del self.incoming_calls[ id_call ]
        return call

class AzzuAccount():
    def __init__( self, username, password, generic_account ):
        "Init of a Azzu Account"
        self.username = username
        self.password = password
        self.generic_account = generic_account
    def register( self ):
        "Create a Azzu Account"
        lib = pj.Lib.instance()
        self.proxy = socket.gethostbyname( 'proxy.azzu.com.br' )
        account_config = pj.AccountConfig( self.proxy, self.username, self.password )
        self.account = lib.create_account( account_config, cb = AccountCallback( self.generic_account ) )
        return self
    def unregister( self ):
        "Unregister this account"
        self.account.delete()
    def call( self, destination, id_call ):
        "Make a call for the destination"
        call_string = 'sip:' + str( destination ) + '@' + self.proxy
        call_callback = CallCallback( self.generic_account.call_listener )
        call = self.account.make_call( call_string, call_callback )
        peanut_call = Call( call, id_call )
        call_callback.peanut_call = peanut_call
        return peanut_call

class AccountListener():
    def __init__( self ):
        "Init an Account Listener"
    def on_register( self, account ):
	"Invoked when the account registred successfully"
        print "Account Registred: Username " + account.delegate.username
    def on_incoming_call( self, account, peanut_call ):
        "Invoked when the account receive an incoming call"
        print "Incoming Call for account with username " + account.delegate.username + "from: " + peanut_call.call.info().remote_uri
#TODO Add here any other usefull listener method!

class AccountCallback( pj.AccountCallback ):
    def __init__( self, peanut_account, account=None, ):
        "Create an Account Callback for the passed account"
        self.peanut_account = peanut_account
        self.listener = peanut_account.listener
        pj.AccountCallback.__init__( self, account )
    def on_incoming_call( self, call ):
        # Register the incomming call into the account 
        self.peanut_account.incoming_call( call )
        #TODO chek if the id is really necessary into the call object
        self.listener.on_incoming_call( self.peanut_account, Call( call, 0 ) )
    def on_reg_state( self ):
        "Register handler"
        if self.account.info().reg_status == 200:
            self.listener.on_register( self.peanut_account )

class Call():
    def __init__( self, call, id ):
        "Create a Call receiving a pjsua call"
        self.call = call
        self.id = id
        self.speak_on_conf = False
    def answer( self ):
        "Answer the call"
        self.call.answer()
    def ring( self ):
        "Return ring status"
        if self.call.info().state == pj.CallState.INCOMING:
            self.call.answer( code = 180 )
    def hangup( self ):
        "Hangup a call from the phone"
        self.call.hangup()
    def dtmf( self, digits ):
        "Send DTMF digits"
        self.call.dial_dtmf( digits )
    def hold( self ):
        "Put this call on hold"
        self.call.hold()
    def unhold( self ):
        "Unhold this call"
        self.call.unhold()
    def mute( self ):
        "Mute this call"
        AudioManager().disconnect_call_audio( self.call )
    def unmute( self ):
        AudioManager().connect_call_audio( self.call )

class CallListener():
    def __init__( self ):
        "Init a Call Listener"
    def on_answer( self, peanut_call ):
        "Invoked when a call is answered"
        print "Call answered from " + peanut_call.call.info().remote_uri
    def on_finished( self, peanut_call ):
        "Invoked when a call is finished"
        print "Call finished from " + peanut_call.call.info().remote_uri
# TODO add more usefull listener methods

class CallCallback( pj.CallCallback ):
    def __init__( self, call_listener, peanut_call=None, call=None ):
        "Create a Call Callback"
        self.call_listener = call_listener
        self.peanut_call = peanut_call
        pj.CallCallback.__init__( self, call )
    def on_state( self ):
        "Intercept any call state change"
        if self.call.info().state == pj.CallState.CONFIRMED:
            self.call_listener.on_answer( self.peanut_call )
        if self.call.info().state == pj.CallState.DISCONNECTED:
            self.call_listener.on_finished( self.peanut_call )
        print 'Call is ', self.call.info().state_text,
        print 'last code =', self.call.info().last_code, 
        print '(' + self.call.info().last_reason + ')'        
    def on_media_state( self ):
        "Intercept any media state change"
        if self.call.info().media_state == pj.MediaState.ACTIVE:
            AudioManager().connect_call_audio( self.call )

class AudioManager():
    def __init__( self ):
        "Init method for AudioManager"
    def connect_call_audio( self, call ):
        "Connect the call slot to the audio device"
        lib = pj.Lib.instance()
        call_slot = call.info().conf_slot
        lib.conf_connect( call_slot, 0 )
        lib.conf_connect( 0, call_slot )
    def connect_conf_audio( self, calls ):
        lib = pj.Lib.instance()
        for c1 in calls:
            if c1.speak_on_conf:
                for c2 in calls:
                    if c1 != c2:
                        slot1 = c1.call.info().conf_slot
                        slot2 = c2.call.info().conf_slot
                        lib.conf_connect( slot1, slot2 )
    def disconnect_call_audio( self, call ):
        lib = pj.Lib.instance()
        call_slot = call.info().conf_slot
        lib.conf_disconnect( call_slot, 0 )
        lib.conf_disconnect( 0, call_slot )

