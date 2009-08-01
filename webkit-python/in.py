from PyQt4.QtCore import QTimer, QVariant, QUrl, SIGNAL
from PyQt4.QtGui import *
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt4.QtWebKit import QWebView
import sys

class NetworkAccessManager(QNetworkAccessManager):

    def __init__(self, old_manager):
    
        QNetworkAccessManager.__init__(self)
        self.old_manager = old_manager
    
    def createRequest(self, operation, request, data):
    
        if operation == self.GetOperation:
            url = request.url()
            print url
            print url.scheme()
            print request.url().encodedHost()
            print url.encodedQueryItemValue( 'username' )
            print url.encodedQueryItemValue( 'password' )
            print url.encodedQueryItems()
        return QNetworkAccessManager.createRequest( self, operation, request )


if __name__ == "__main__":

    app = QApplication(sys.argv)
    view = QWebView()
    
    old_manager = view.page().networkAccessManager()
    new_manager = NetworkAccessManager(old_manager)
    view.page().setNetworkAccessManager(new_manager)
    view.resize(200,200) 
    view.load(QUrl("a.html")) 
    view.show()
    sys.exit(app.exec_())
