"""
	Author: Andre Ribeiro Goncalves
"""


class LazyProxy:
	""" 
		Lazy load an object. 
	"""	
	def __init__(self, clazz, *args, **kw):
		self.__dict__['clazz'] = clazz
		self.__dict__['args'] = args
		self.__dict__['kw'] = kw
		self.__dict__['obj'] = None

	"""
		If an object is not instantiated, calls init
	"""
	def instantiate(self):
		if self.obj is None:
			print 'instantiating now'
			self.__dict__['obj'] = self.clazz(*self.args, **self.kw)


	"""
		Intercepts any get
	"""
	def __getattr__(self,name):
		self.instantiate()
		return getattr(self.obj,name)

	"""
		Intercepts any set
	"""
	def __setattr__(self,name, value):
		self.instantiate()
		setattr(self.obj, name, value)
	
	"""
		Represents the object. If the target is not instantiated, show a custom message. If it was instantiated, delegates the call
	"""
	def __repr__(self):
		if self.obj is None:
			return 'Lazy proxy of: ' + str(self.clazz)
		return str(self.obj)

	"""
		If the callee tries to 'recreate' the object, calls init in the target
	"""
	def __call__(self, *args):
		if self.obj is None:
			self.__dict__['obj'] = self.clazz( *args )
		return self.obj

	"""
		String builtin representation of the object. If the target is not instantiated, show a custom message. If it was instantiated, delegates the call
	"""
	def __str__(self):
		if self.obj is None:
			return 'Lazy proxy of: ' + str(self.clazz)
		return str(self.obj)

# Lazy Load a class
def Lazy(clazz):
	def newf( *args, **kw ):
		print 'Creating Lazy Proxy for class: ' + str(clazz)
		return LazyProxy(clazz, *args, **kw)
	return newf

@Lazy
class A:
	def __init__(self, a):
		self.a = a
	
	def do(self, x):
		print self.a + ' doing: ' + x
	def __repr__(self):
		return "Eu sou o A =)"


