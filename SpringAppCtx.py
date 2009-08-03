from springpython.config import PythonConfig
from springpython.config import Object
from springpython.context import scope
from action import *
from PyQt4.QtWebKit import QWebView
from Web import *

class ActionBasedApplicationContext(PythonConfig):
    def __init__(self):
        super(ActionBasedApplicationContext, self).__init__()
        
    @Object(scope.SINGLETON)
    def Account(self):
	account = Account()
	account.view = self.View()
        self.logger.debug("Description = %s" % account)
        return account

    @Object(scope.SINGLETON)
    def NetworkAccessManager(self):
	n = NetworkAccessManager()
	n.view = self.View()
	n.actions = { str(Account).split(".")[-1:][0] : self.Account() }
	return n

    @Object(scope.SINGLETON)
    def View(self):
	return  WebView()

