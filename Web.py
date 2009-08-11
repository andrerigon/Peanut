import traceback, os
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PyQt4.QtWebKit import QWebView
from PyQt4.QtCore import QUrl, QTimer, QVariant, SIGNAL, QString
from PyQt4.QtGui import *
from action import *
from spring import *
import logging

class WebView(QWebView):
	
	def __init__(self):
		self.log = logging.getLogger(self.__class__.__name__)
		QWebView.__init__(self);
		
	def go(self, url):
		self.runJavaScript("go('"+(url)+"')")
	
	def msg(self, message):
		self.runJavaScript("showMessage('"+(message)+"')")
		
	def runJavaScript(self, script):
		self.log.debug("run javascript: "+script)
		self.page().mainFrame().evaluateJavaScript(QString(str(script)));

class HtmlReply(QNetworkReply):

	def __init__(self, url, operation, html):

		QNetworkReply.__init__(self)
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
		self.log = logging.getLogger(self.__class__.__name__)
		self.view = None 
		self.actions = None
		QNetworkAccessManager.__init__(self)
	
	def createRequest(self, operation, request, data):
	
		url = request.url()

		#print url

		if operation == self.GetOperation:
			
			actionName = str(url.scheme())
			methodName = str(url.encodedHost())

			is_action = False
			
			if url.scheme() == 'file':
				is_action = str(url.toEncoded()).endswith(".action")
				if is_action is False:
					return QNetworkAccessManager.createRequest( self, operation, request )
			
			if is_action:
				fileAction = str(url.toEncoded()).rpartition("/")[2].split(".")
				actionName = fileAction[0]
				methodName = fileAction[1]
						
			result = self.__invokeAction(actionName, methodName, url)
			
			if result is not None:
				return HtmlReply(url, operation, result)
			
			return QNetworkAccessManager.createRequest( self, operation, request )
			

	def __invokeAction(self, actionName, methodName, url):
		#TODO review to try catch and logs
		
		self.log.debug("try to invoke method '"+(methodName)+"' in action '"+(actionName)+"'.")
		
		action = self.actions[actionName]
		self.bindParameters(action, url.encodedQueryItems())
				
		try:
			method = getattr(action, methodName)
			return method()
		
		except Exception,e:
			self.view.msg("ERRO inesperado")
			self.log.debug("ERROR: OPS, fail to invoke method '"+(methodName)+"' in action '"+(actionName)+"'.")
			self.log.debug(traceback.print_exc())
		

	def bindParameters(self, action, params_request):
		if len(params_request) > 0:
			self.log.debug("Bind parametes to object")
		for param in params_request:
			self.log.debug(param[0]+" = "+ param[1])
			setattr(action, str(param[0]), str(param[1]))


	def start(self):
		self.old_manager = self.view.page().networkAccessManager()
		self.view.page().setNetworkAccessManager(self)	
		self.view.resize(380,280) 	
		self.view.load(QUrl("App.start.action"))
		self.view.show()



