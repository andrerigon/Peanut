from Peanut import Phone, AccountListener, CallListener
import re

class Action:
	pass

class Account(Action):
	
	__acc = None
	__call = None
	__phone = None
	
	def register(self):
		self.__acc = self.__getPhone().register( self.username, self.password, WebKitAccountListener(self.view), WebKitCallListener(self.view))
		
	def unregister(self):
		#TODO nao deveria ser com um listener?
		self.__acc.unregister()
		#TODO e assim mesmo?
		#self.__getPhone().stop()
		self.view.go('login.html')
		
	def call(self):
		self.__call = self.__acc.call( self.destination )
	
	def answer(self):
		self.__call.answer()
	
	def hangup(self):
		self.__call.hangup()
	
	def balance(self):
		self.view.msg("TODO: implement R$ 0,00")
	
	def __getPhone(self):
		if self.__phone is None:
			self.__phone = Phone().start();
		return self.__phone;

class WebKitAccountListener(AccountListener):
	
	def __init__(self, view):
		self.view = view
	
	def on_register_success(self, account):
		self.view.go('home.html')
		
	def on_register_error( self, account ):
		self.view.msg("Falha ao registrar.")
		
	def on_incoming_call( self, account, peanut_call ):
		
		regex = re.match('<sip:(\d+)@.*', str(peanut_call.call.info().remote_uri))
		msg = regex.group(1) + " esta chamando" 
		self.view.msg(msg)
		AccountListener.on_incoming_call(self, account, peanut_call )

class WebKitCallListener(CallListener):	
	
	def __init__(self, view):
		self.view = view
		
	def on_answer(self, peanut_call):
		self.view.msg("Chamada Atendida.")
		CallListener.on_answer(self, peanut_call)
		
	def on_finished( self, peanut_call ):
		self.view.msg("Chamada Desligada.")
		CallListener.on_finished( self, peanut_call )
	
