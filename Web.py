from PyQt4.QtWebKit import QWebView
from PyQt4.QtNetwork import QNetworkAccessManager
from PyQt4.QtWebKit import QWebView
from PyQt4.QtCore import QTimer, QVariant, QUrl, SIGNAL
from PyQt4.QtGui import *
import sys, traceback

class WebView(QWebView):
	
	def go(self, url):
		self.__runJavaScript("go('"+(url)+"')")
	
	def msg(self, message):
		self.__runJavaScript("showMessage('"+(message)+"')")
		
	def __runJavaScript(self, script):
		self.page().mainFrame().evaluateJavaScript(script);

class NetworkAccessManager(QNetworkAccessManager):
	
	def __init__(self):
		self.view = None 
		self.actions = None
		
		QNetworkAccessManager.__init__(self)
	
	def createRequest(self, operation, request, data):
		
		url = request.url()
		protocol = str(url.scheme())
		host = str(url.encodedHost())

		if protocol == 'file':
		   return QNetworkAccessManager.createRequest( self, operation, request )

		if operation == self.GetOperation:
			
			#TODO review to try catch and logs
			
			print "DEBUG: try to invoke method '"+(host)+"' in action '"+(protocol)+"'."
			
			try:
				action = getattr(self, protocol)
				print "DEBUG: get action '"+(protocol)+"' in cache - simple attribute class"
			except AttributeError, ae:
				try:
					print "DEBUG: create new instance to action '"+(protocol)+"'."
					action = self.actions[protocol]
					setattr(self, protocol, action)
				except Exception,e:
					self.view.msg("ERRO inesperado")
					print "ERROR: OPS, fail to create instance do class '"+(protocol)+"' action."
					traceback.print_exc()
		
			self.bindParameters(action, url)
					
			try:
				method = getattr(action, host)
				method()
			except Exception,e:
				self.view.msg("ERRO inesperado")
				print "ERROR: OPS, fail to invoke method '"+(host)+"' in action '"+(protocol)+"'."
				traceback.print_exc()
				

		return QNetworkAccessManager.createRequest( self, operation, request )

	def bindParameters( self, action, url ):
		print "DEBUG: Bind parametes to object"
		for param in url.encodedQueryItems():
			print  param[0]+" = "+ param[1]
			setattr(action, str(param[0]), str(param[1]))

	def start(self):
		self.old_manager = self.view.page().networkAccessManager()
		self.view.page().setNetworkAccessManager(self)		
		self.view.resize(280,180) 
		self.view.load(QUrl("resources/login.html")) 
		self.view.show()

