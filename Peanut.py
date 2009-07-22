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
        account = GenericAccount( username, password )
        account.register()
        return account

class GenericAccount():
    def __init__( self, username, password ):
        "Init of GenericAccount"
        self.incoming_calls = {} 
        self.id_call = 0
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
        call_callback = CallCallback( call )
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
        callString = 'sip:' + str( destination ) + '@' + self.proxy
        call = self.account.make_call( callString, CallCallback() )
        return Call( call, id_call )

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

class AccountCallback( pj.AccountCallback ):
    def __init__( self, peanut_account, account=None, ):
        "Create an Account Callback for the passed phone"
        self.peanut_account = peanut_account
        pj.AccountCallback.__init__( self, account )
    def on_incoming_call( self, call ):
        # Register the incomming call into the phone
        self.peanut_account.incoming_call( call )
    def on_reg_state( self ):
        "Register finished handler"
        print 'Registration complete, status=', self.account.info().reg_status, \
              '(' + self.account.info().reg_reason + ')'

class CallCallback( pj.CallCallback ):
    def __init__( self, call=None ):
        "Create a Call Callback"
        pj.CallCallback.__init__( self, call )
    def on_state(self):
        "Intercept any call state change"
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

