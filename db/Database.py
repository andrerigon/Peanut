import shelve
class ProfileDb():
	
	def open(self):
		self.__db = shelve.open("db/profiles.db")
	
	def close(self):
		self.__db.close()
		
	def add(self, profile):
		self.__db[profile.name] = profile;
	
	def size(self):
		return len(self.__db)
		
	def find_all(self):
		return self.__db.values();
		
	def get(self, key):
		return self.__db[key]
		
	def get_first(self):
		return self.get(self.__db.keys()[0])
		