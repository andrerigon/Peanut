import pjsua as pj
import socket
import md5

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

    def register( self, username, password, account_type = 'azzu', account_listener = None, call_listener = None ):
        "Make an account register"
        if account_listener == None:
            account_listener = AccountListener()
        if call_listener == None:
            call_listener = CallListener()
            
        account_key = GenericAccount.account_key( username, account_type )
            
        # TODO do this with spring 
        delegate_account = AzzuAccount( username, password )
        account = GenericAccount( account_key, account_listener, call_listener, delegate_account )
        
        self.accounts[ account_key ] = account
        
        account.register()
        
        return account
    
    def unregister( self, username, account_type = 'azzu' ):
        account_key = GenericAccount.account_key( username, account_type )
        self.accounts.pop( account_key ).unregister()
    
    def get_account( self, username, account_type = 'azzu' ):
        account_key = GenericAccount.account_key( username, account_type )
        return self.accounts[ account_key ]


class GenericAccount():

    def __init__( self, key, listener, call_listener, delegate ):
        "Init of GenericAccount"
        self.key = key
        self.listener = listener
        self.call_listener = call_listener
        self.registered = False
        self.delegate = delegate
        self.calls = {}
        
    def get_call( self, destination ):
        call_key = Call.call_key( self.key, destination )
        return calls[ call_key ]

    def register( self ):
        "Register this account"
        self.listener.on_register_request( self )
        self.delegate = self.delegate.register( self )
        return self

    def register_success( self ):
        "Invoked when this account registred successfully"
        self.registered = True
        self.listener.on_register_success( self )

    def register_error( self ):
        self.registered = False
        "Invoked when this account has an error during its register"
        self.listener.on_register_error( self )

    def unregister( self ):
        self.delegate.unregister()
        self.registered = False
        self.listener.on_unregister( self )

    def call( self, destination ):
        peanut_call = self.delegate.call( destination, self )
        self.calls[ peanut_call.destination() ] = peanut_call
        return peanut_call

    def incoming_call( self, call ):
        "Register incoming call to the account"
        peanut_call = Call( call )
        
        # Register call
        self.calls[ peanut_call.destination() ] = peanut_call
        
        # Create Call Callback
        call_callback = CallCallback( self, peanut_call )
        call.set_callback( call_callback )
        
        # Answer with a ring
        peanut_call.ring()
        
        # Trigger incoming call event
        self.listener.on_incoming_call( self, peanut_call )
        
    def answer_call( self, destination ):
        self.calls[ destination ].answer()
        
    def hangup_call( self, destination ):
        self.calls[ destination ].hangup()
        
    def unregister_call( self, peanut_call ):
        self.calls.pop( peanut_call.destination() )

    @staticmethod
    def account_key( username, account_type ):
        string_key = str( username ) + str( account_type )
        return md5.md5( string_key ).hexdigest()


class AzzuAccount():

    def __init__( self, username, password ):
        "Init of a Azzu Account"
        self.username = str( username )
        self.password = str( password )

    def register( self, generic_account ):
        "Create a Azzu Account"
        lib = pj.Lib.instance()
        self.proxy = socket.gethostbyname( 'proxy.azzu.com.br' )
        account_config = pj.AccountConfig( self.proxy, self.username, self.password )
        self.account = lib.create_account( account_config, cb = AccountCallback( generic_account ) )
        return self

    def unregister( self ):
        "Unregister this account"
        self.account.delete()

    def call( self, destination, generic_account ):
        "Make a call for the destination"
        call_string = 'sip:' + str( destination ) + '@' + self.proxy
        call_callback = CallCallback( generic_account )
        call = self.account.make_call( call_string, call_callback )
        return Call( call )


class AccountListener():

    def __init__( self ):
        "Init an Account Listener"

    def on_register_request( self, account ):
        "Invoked when the account register is requested"
        print 'Account Register requested: username ' + account.delegate.username

    def on_register_success( self, account ):
	"Invoked when the account registred successfully"
        print 'Account Registred: username ' + account.delegate.username

    def on_register_error( self, account ):
        "Invoked when the account has a regiter error"
        print 'Error Registering the Account: username ' + account.delegate.username

    def on_unregister( self, account ):
        "Invoked when the account was unregistered"
        print 'Account Unregistered: username ' + account.delegate.username

    def on_incoming_call( self, account, peanut_call ):
        "Invoked when the account receive an incoming call"
        print 'Incoming Call for account with username ' + account.delegate.username + ' from: ' + peanut_call.call.info().remote_uri


class AccountCallback( pj.AccountCallback ):

    def __init__( self, peanut_account, account=None, ):
        "Create an Account Callback for the passed account"
        self.peanut_account = peanut_account
        pj.AccountCallback.__init__( self, account )

    def on_incoming_call( self, call ):
        # Register the incomming call into the account 
        self.peanut_account.incoming_call( call )

    def on_reg_state( self ):
        "Register handler"
        print 'reg_status: ' + str( self.account.info().reg_status ) + ' reason: ' + self.account.info().reg_reason
        if self.account.info().reg_status == 200:
            self.peanut_account.register_success()
        if self.account.info().reg_status > 700:
            self.peanut_account.register_error()


class Call():

    def __init__( self, call ):
        "Create a Call receiving a pjsua call"
        self.call = call
        self.speak_on_conf = False
        
    def destination( self ):
        return self.call.info().remote_uri

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
        AudioManager().disconnect_output_audio( self.call )
        return self

    def unmute( self ):
        AudioManager().connect_output_audio( self.call )
        return self
    

class CallListener():

    def __init__( self ):
        "Init a Call Listener"

    def on_calling( self, peanut_account, peanut_call ):
        "Invoked when a call is started but is not connected or finished"
        print 'Trying to call to ' + peanut_call.call.info().remote_uri

    def on_ringing( self, peanut_account, peanut_call ):
        "Invoked when a call is in ringing status"
        print 'Ringing call with ' + peanut_call.call.info().remote_uri

    def on_connecting( self, peanut_account, peanut_call ):
        "Invoked when a call is connecting"
        print 'Connecting call with ' + peanut_call.call.info().remote_uri

    def on_answer( self, peanut_account, peanut_call ):
        "Invoked when a call is answered"
        print 'Call answered with ' + peanut_call.call.info().remote_uri

    def on_finished( self, peanut_account, peanut_call ):
        "Invoked when a call is finished"
        peanut_account.unregister_call( peanut_call )
        print 'Call finished with ' + peanut_call.call.info().remote_uri
# TODO add more usefull listener methods


class CallCallback( pj.CallCallback ):

    def __init__( self, peanut_account, peanut_call=None, call=None ):
        "Create a Call Callback"
        self.call_listener = peanut_account.call_listener
        self.peanut_account = peanut_account
        self.peanut_call = peanut_call
        pj.CallCallback.__init__( self, call )

    def on_state( self ):
        "Intercept any call state change"
        if self.peanut_call == None:
            self.peanut_call = Call( self.call )
        # State where an outcoming call has just been requested
        if self.call.info().state == pj.CallState.CALLING:
            self.call_listener.on_calling( self.peanut_account, self.peanut_call )
        # State where a call is in ringing
        if self.call.info().state == pj.CallState.EARLY:
            self.call_listener.on_ringing( self.peanut_account, self.peanut_call )
        # State where a call was received and is almost confirmed
        if self.call.info().state == pj.CallState.CONNECTING:
            self.call_listener.on_connecting( self.peanut_account, self.peanut_call )
        # State where a call is answered and confiremd
        if self.call.info().state == pj.CallState.CONFIRMED:
            self.call_listener.on_answer( self.peanut_account, self.peanut_call )
        # State where a call is finished and disconnected
        if self.call.info().state == pj.CallState.DISCONNECTED:
            self.call_listener.on_finished( self.peanut_account, self.peanut_call )

    def on_media_state( self ):
        "Intercept any media state change"
        if self.call.info().media_state == pj.MediaState.ACTIVE:
            AudioManager().connect_call_audio( self.call )


class AudioManager():

    def __init__( self ):
        "Init method for AudioManager"

    def connect_conf_audio( self, calls ):
        "Connect the slots to make a conference"
        lib = pj.Lib.instance()
        for c1 in calls:
            if c1.speak_on_conf:
                for c2 in calls:
                    if c1 != c2:
                        slot1 = c1.call.info().conf_slot
                        slot2 = c2.call.info().conf_slot
                        lib.conf_connect( slot1, slot2 )

    def connect_call_audio( self, call ):
        "Connect the call slot to the audio device"
        lib = pj.Lib.instance()
        call_slot = call.info().conf_slot
        lib.conf_connect( call_slot, 0 )
        lib.conf_connect( 0, call_slot )

    def disconnect_call_audio( self, call ):
        "Disconnect the call slot to the audio device"
        lib = pj.Lib.instance()
        call_slot = call.info().conf_slot
        lib.conf_disconnect( call_slot, 0 )
        lib.conf_disconnect( 0, call_slot )

    def connect_output_audio( self, call ):
        "Connect only de output slot to the call slot"
        lib = pj.Lib.instance()
        call_slot = call.info().conf_slot
        lib.conf_connect( 0, call_slot )

    def disconnect_output_audio( self, call ):
        "Disconnect only de output slot to the call slot"
        lib = pj.Lib.instance()
        call_slot = call.info().conf_slot
        lib.conf_disconnect( 0, call_slot )

    def list_audio_devices( self ):
        "List all the audio devices into the system"
        lib = pj.Lib.instance()
        devices = lib.enum_snd_dev()
        peanut_devices = []
        i = 0
        for dev in devices:
            peanut_devices.append( AudioDevice( dev, i ) )
            i += 1
        return peanut_devices

    def set_audio_devices( self, input, output ):
        "Set the input and the output device for the PeanutPhone"
        lib = pj.Lib.instance()
        lib.set_snd_dev( input.id, output.id )

        
class AudioDevice():

    def __init__( self, device, id ):
        "Initialize a Peanut AudioDevice wrapper class"
        self.device = device
        self.id = id

    def is_output( self ):
        "Returns true if this is an output device"
        return self.device.output_channels > 0

    def is_input( self ):
        "Return true if this is an input device"
        return self.device.input_channels > 0

    def device_type( self ):
        "Return a string that describes the type of the device"
        if self.is_output():
            return 'OUTPUT'
        elif self.is_input():
            return 'INPUT'
        return 'NULL'
            
    def is_active( self ):
        "Return true if this device is currently used by the phone"
        lib = pj.Lib.instance()
        active_ids = lib.get_snd_dev()
        if self.is_input():
            return self.id == active_ids[0]
        elif self.is_output():
            return self.id == active_ids[1]
        return False

    def name( self ):
        "Returns the name of the device"
        return self.device.name

    def __str__( self ):
        return 'Device { id:' + str( self.id ) + ', name:' + self.name() + \
        ', active: ' + str( self.is_active() ) + ', type:' + self.device_type() + '}'
        
