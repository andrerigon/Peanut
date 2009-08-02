from PyQt4.QtCore import QTimer, QVariant, QUrl, SIGNAL
from PyQt4.QtGui import *
from PyQt4.QtNetwork import QNetworkAccessManager
from PyQt4.QtWebKit import QWebView
from Actions import *
import sys, traceback
from Peanut import Phone

class NetworkAccessManager(QNetworkAccessManager):
	
	def __init__(self, old_manager, view ):
	
		QNetworkAccessManager.__init__(self)
		self.old_manager = old_manager
		self.__view = view
	
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
					action = eval(protocol)()
					action.setView(self.__view)
					setattr(self, protocol, action)
				except Exception,e:
					self.__view.msg("ERRO inesperado")
					print "ERROR: OPS, fail to create instance do class '"+(protocol)+"' action."
					traceback.print_exc()
		
			action.automaticBindParameters(url)
					
			try:
				method = getattr(action, host)
				method()
			except Exception,e:
				self.__view.msg("ERRO inesperado")
				print "ERROR: OPS, fail to invoke method '"+(host)+"' in action '"+(protocol)+"'."
				traceback.print_exc()
				

		return QNetworkAccessManager.createRequest( self, operation, request )
	

class WebView(QWebView):
	
	def go(self, url):
		self.__runJavaScript("go('"+(url)+"')")
	
	def msg(self, message):
		self.__runJavaScript("showMessage('"+(message)+"')")
		
	def __runJavaScript(self, script):
		self.page().mainFrame().evaluateJavaScript(script);


if __name__ == "__main__":

	app = QApplication(sys.argv)
	view = WebView()
	old_manager = view.page().networkAccessManager()
	new_manager = NetworkAccessManager(old_manager, view)
	view.page().setNetworkAccessManager(new_manager)
	view.resize(280,180) 
	view.load(QUrl("resources/login.html")) 
	view.show()
	sys.exit(app.exec_())
