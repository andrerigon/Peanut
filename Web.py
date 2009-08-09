import traceback, os
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PyQt4.QtWebKit import QWebView
from PyQt4.QtCore import QUrl, QTimer, QVariant, SIGNAL
from PyQt4.QtGui import *
from action import *

class WebView(QWebView):
	
	def go(self, url):
		self.__runJavaScript("go('"+(url)+"')")
	
	def msg(self, message):
		self.__runJavaScript("showMessage('"+(message)+"')")
		
	def parse(self, html):
		self.page().mainFrame().setHtml(html)
		
	def __runJavaScript(self, script):
		self.page().mainFrame().evaluateJavaScript(script);

class HtmlReply(QNetworkReply):

	def __init__(self, url, operation, html):

		QNetworkReply.__init__(self)
		#print html
		self.content = html
		self.offset = 0
		self.setHeader(QNetworkRequest.ContentTypeHeader, QVariant("text/html; charset=utf-8"))
		self.setHeader(QNetworkRequest.ContentLengthHeader, QVariant(len(self.content)))
		QTimer.singleShot(0, self, SIGNAL("readyRead()"))
		QTimer.singleShot(0, self, SIGNAL("finished()"))
		self.open(self.ReadOnly | self.Unbuffered)
		self.setUrl(url)

	def abort(self):
		pass

	def bytesAvailable(self):
		return len(self.content) - self.offset

	def isSequential(self):
		return True

	def readData(self, maxSize):
		if self.offset < len(self.content):
			end = min(self.offset + maxSize, len(self.content))
			data = self.content[self.offset:end]
			self.offset = end
			return data

class NetworkAccessManager(QNetworkAccessManager):
	
	def __init__(self):
		self.view = None 
		self.actions = None
		QNetworkAccessManager.__init__(self)
	
	def createRequest(self, operation, request, data):
	
		url = request.url()

		print url

		if operation == self.GetOperation:
			
			actionName = str(url.scheme())
			methodName = str(url.encodedHost())

			is_action = False
			
			if url.scheme() == 'file':
				is_action = str(url.toEncoded()).endswith(".action")
				if is_action is False:
					return QNetworkAccessManager.createRequest( self, operation, request )
			
			if is_action:
				fileAction = str(url.toEncoded()).rpartition(os.sep)[2].split(".")
				actionName = fileAction[0]
				methodName = fileAction[1]
						
			result = self.__invokeAction(actionName, methodName, url)
			
			if result is not None:
				return HtmlReply(url, operation, result)
			
			return QNetworkAccessManager.createRequest( self, operation, request )
			

	def __invokeAction(self, actionName, methodName, url):
		#TODO review to try catch and logs
		
		print "DEBUG: try to invoke method '"+(methodName)+"' in action '"+(actionName)+"'."
		
		try:
			action = getattr(self, actionName)
			print "DEBUG: get action '"+(actionName)+"' in cache - simple attribute class"
		except AttributeError, ae:
			try:
				print "DEBUG: create new instance to action '"+(actionName)+"'."
				action = self.get_action(actionName)
				setattr(self, methodName, actionName)
			except Exception,e:
				self.view.msg("ERRO inesperado")
				print "ERROR: OPS, fail to create instance do class '"+(actionName)+"' action."
				traceback.print_exc()
	
		self.bindParameters(action, url)
				
		try:
			method = getattr(action, methodName)
			return method()
		
		except Exception,e:
			self.view.msg("ERRO inesperado")
			print "ERROR: OPS, fail to invoke method '"+(methodName)+"' in action '"+(actionName)+"'."
			traceback.print_exc()		
		

	def bindParameters( self, action, url ):
		print "DEBUG: Bind parametes to object"
		for param in url.encodedQueryItems():
			print  param[0]+" = "+ param[1]
			setattr(action, str(param[0]), str(param[1]))

	def get_action( self, actionName ):
		try:
			clazz = getattr(Actions, actionName)
			action = clazz()
			action.view = self.view
			
		except AttributeError, ae:
			print("action not found: "+actionName)			
		return action
		

	def start(self):
		self.old_manager = self.view.page().networkAccessManager()
		self.view.page().setNetworkAccessManager(self)	
		self.view.resize(380,280) 	
		#self.view.resize(280,180)
		self.view.load(QUrl("App.start.action"))
		
		self.view.show()



