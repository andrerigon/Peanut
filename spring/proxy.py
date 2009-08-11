import time
from types import MethodType
import sys
import logging

"""
	Author: Andre Ribeiro Goncalves
"""


class LazyProxy():
	
	""" 
		Lazy load an object. 
	"""	
	def __init__(self, clazz, *args, **kw):
		self.__dict__['logger'] = logging.getLogger(str(clazz))
		self.__dict__['clazz'] = clazz
		self.__dict__['args'] = args
		self.__dict__['kw'] = kw
		self.__dict__['target'] = None
		self.__dict__['properties'] = {}

	"""
		If an object is not instantiated, calls init
	"""
	def instantiate(self):
		if self.target is None:
			self.logger.debug( 'instantiating now' )
			self.__dict__['target'] = self.clazz(*self.args, **self.kw)
			for key in self.properties.keys():
				self.target.__dict__[key] = self.properties[key]


	"""
		Intercepts any get
	"""
	def __getattr__ (self,name):
		self.instantiate()
		attr = getattr(self.target, name)
		if type(attr) == MethodType:
			return lambda *args, **kwargs: self.__wrap(name, args, kwargs)
		else:
			return attr
		
	def __wrap(self, name, args, kwargs):
		self.logger.debug( "Calling method: " + name + " with params: " + str( args ) )
		now = time.time()
		result = getattr(self.target, name)( *args, **kwargs)
		now = time.time() - now
		self.logger.debug( "Method " + name + " run in " + str(now)  + "s" )
		self.logger.debug( "Result:\n" + str(result) )
		return result

	"""
		Intercepts any set
	"""
	def __setattr__(self,name, value):
		if self.target is None:
			self.__dict__['properties'][name] = value
		else:
			setattr(self.target, name, value)
	
	"""
		Represents the object. If the target is not instantiated, show a custom message. If it was instantiated, delegates the call
	"""
	def __repr__(self):
		if self.target is None:
			return 'Lazy proxy of: ' + str(self.clazz)
		return str(self.target)

	"""
		If the callee tries to 'recreate' the object, calls init in the target
	"""
	def __call__(self, *args):
		if self.target is None:
			self.__dict__['target'] = self.clazz( *args )
		return self.target

	"""
		String builtin representation of the object. If the target is not instantiated, show a custom message. If it was instantiated, delegates the call
	"""
	def __str__(self):
		if self.target is None:
			return 'Lazy proxy of: ' + str(self.clazz)
		return str(self.target)

# Lazy Load a class
def Lazy(clazz):
	class Proxy( LazyProxy, clazz ):
		def __init__(self,*args, **kw):
			print 'Creating Lazy Proxy for class: ' + str(clazz)
			LazyProxy.__init__(self,clazz, *args, **kw)
	return Proxy

@Lazy
class A():
	def __init__(self, a):
		self.a = a
	
	def do(self, x):
		print self.a + ' doing: ' + x
	def __repr__(self):
		return "Eu sou o A =)"


