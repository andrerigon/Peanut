import random
import unittest
from PyQt4.QtCore import QTimer, QVariant, QUrl, SIGNAL
from PyQt4.QtGui import *
from PyQt4.QtNetwork import QNetworkAccessManager
from PyQt4.QtWebKit import QWebView
from init import NetworkAccessManager
from init import WebView
import sys, traceback


class TestAction(unittest.TestCase):

   def testUrl(self):
	app = QApplication(sys.argv)
	view = WebView()
	old_manager = view.page().networkAccessManager()
	new_manager = NetworkAccessManager(old_manager, view)
	self.assertRaises( AttributeError, new_manager.createRequest, QNetworkAccessManager.GetOperation, QUrl('coco'), 'aaaaaaaa' )
	#new_manager.createRequest( QNetworkAccessManager.GetOperation, QUrl('coco'), 'aaaaaaaa' )
	

if __name__ == '__main__':
    unittest.main()

