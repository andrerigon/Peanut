from PyQt4.QtCore import QTimer, QVariant, QUrl, SIGNAL
from PyQt4.QtGui import *
from action import *
import sys, traceback
from Peanut import Phone
from spring import  *
from springpython.context import ApplicationContext
from Web import *

if __name__ == "__main__":
	app = QApplication(sys.argv)
	fact = ApplicationContext(ActionBasedApplicationContext())
	fact.get_object('NetworkAccessManager').start()
	sys.exit(app.exec_())

