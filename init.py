import sys
import signal
import os
from PyQt4.QtGui import QApplication
from spring import  *
from springpython.context import ApplicationContext

if __name__ == "__main__":
	app = QApplication(sys.argv)
	fact = ApplicationContext(ActionBasedApplicationContext())
	fact.get_object('NetworkAccessManager').start()
	app.setQuitOnLastWindowClosed(True)
	def exitAll():
		os.killpg(os.getpgrp(), signal.SIGINT)
	def handler(sig, arg):
		print "Saindooooooo"
		app.exit()
	signal.signal(signal.SIGINT,handler)
	app.connect(app, SIGNAL("lastWindowClosed()"), exitAll)
	sys.exit(app.exec_())

