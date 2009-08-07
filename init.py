import sys
from PyQt4.QtGui import QApplication
from SpringAppCtx import ActionBasedApplicationContext
from springpython.context import ApplicationContext

if __name__ == "__main__":
	app = QApplication(sys.argv)
	fact = ApplicationContext(ActionBasedApplicationContext())
	fact.get_object('NetworkAccessManager').start()
	sys.exit(app.exec_())

