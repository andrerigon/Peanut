from Peanut import Phone, AccountListener, CallListener
from Cheetah.Template import Template
from db import ProfileDb, Profile
from spring import *

class Action(object):
	pass

#@Lazy
class Account(Action):
	
	__phone = None
	__profile = None
	
	def register(self):
		db = ProfileDb()
		db.open()
		self.__profile = db.get(self.profileName)
		if self.__profile is None:
			self.view.msg("Fail to register, invalid profile")
		else:
			self.__get_phone().register( self.__profile.username, self.__profile.password, self.__profile.type, WebKitAccountListener(self.view), WebKitCallListener(self.view))
		db.close()
		
	def unregister(self):
		self.__get_phone().unregister(self.__profile.username, self.__profile.type)
		self.view.go('App.start.action')
		
	def call(self):
		self.__account().call( self.destination )
	
	def answer(self):
		self.__account().answer_call( self.destination )
	
	def hangup(self):
		self.__call.hangup()
	
	def balance(self):
		self.view.msg("TODO: implement R$ 0,00")
	
	def __account(self):
		return self.__get_phone().get_account(self.__profile.username, self.profile.type)
	
	def __get_phone(self):
		if self.__phone is None:
			self.__phone = Phone().start();
		return self.__phone;

#@Lazy
class App(Action):
	
	def start(self):
		db = ProfileDb()
		db.open()
		
		if db.size() == 0:
			return ProfileManager().new()
		else:
			if db.size() == 1:
				profile = db.get_first()
				if profile.auto_login == 'on':
					print "Register and redirect"
					return
			
		template = Template(file="web/profile_select.tpl")
		template.profiles = db.find_all()
		db.close()
		return str(template)
		
	def home(self):
		template = Template(file="web/home.tpl")
		return str(template)

#@Lazy
class ProfileManager(Action):

	def new(self):
		template = Template(file="web/profile_new.tpl")
		return str(template)

	def save(self):
		db = ProfileDb()
		db.open()
		if hasattr(self, 'auto_login') is False:
			self.auto_login = 'off'
		profile = Profile(self.name, self.type, self.username, self.password, self.auto_login)
		db.add(profile)
		db.close()
		self.view.go("App.start.action")


class WebKitAccountListener(AccountListener):
	
	def __init__(self, view):
		self.view = view
	
	def on_register_success(self, account):
		self.view.go('App.home.action')
		
	def on_register_error( self, account ):
		self.view.msg("Falha ao registrar.")
		
	def on_incoming_call( self, account, peanut_call ):
		self.view.runJavaScript("CallListener.incomming_call('"+(peanut_call.destination())+"')")
		AccountListener.on_incoming_call(self, account, peanut_call )

class WebKitCallListener(CallListener):	
	
	def __init__(self, view):
		self.view = view
		
	def on_answer(self, peanut_account, peanut_call):
		self.view.msg("Chamada Atendida.")
		CallListener.on_answer(self, peanut_account, peanut_call)
		
	def on_finished( self, peanut_account, peanut_call ):
		self.view.msg("Chamada Desligada.")
		CallListener.on_finished( self, peanut_account, peanut_call )
		
		
	
