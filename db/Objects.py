class Profile():
	
	def __init__(self, name, type, username, password=None, auto_login=0):
		self.name = name
		self.type = type
		self.username = username
		self.password = password
		self.auto_login = auto_login
		
		
