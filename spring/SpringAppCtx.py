from springpython.config import PythonConfig
from springpython.config import Object
from springpython.context import scope
from action import *
from PyQt4.QtWebKit import QWebView
from Web import *
from spring import *
import inspect

class ActionBasedApplicationContext(PythonConfig):
    def __init__(self):
	self.view = WebView()
        super(ActionBasedApplicationContext, self).__init__()
	for arg in sys.argv: 
		if arg == "--debug":
			logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s")

    @Object(scope.SINGLETON)
    def NetworkAccessManager(self):
	n = NetworkAccessManager()
	n.view = self.view 
	n.actions = self.Actions()
	return n

    def Actions(self):
		dict = {}
		for name in dir(Actions):
			clazz = getattr(Actions, name)
			if isinstance(clazz, type) and issubclass(clazz, Actions.Action):
			#if inspect.isclass(clazz) and issubclass(clazz, Actions.Action):
				#action = clazz()
				action = LazyProxy(clazz)
				action.view = self.view 
				dict[name] = action
		return dict
