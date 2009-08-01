from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from PyQt4.QtCore import QUrl
import sys
app = QApplication(sys.argv)
browser = QWebView()
browser.show()
browser.resize(200,200)
browser.load(QUrl("a.html"))
body = browser.page().mainFrame().evaluateJavaScript("alert('Ola Mundo')")

