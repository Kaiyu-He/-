# Form implementation generated from reading ui file 'log_in.ui'
#
# Created by: PyQt6 UI code generator 6.7.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_login(object):
    def setupUi_login(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(356, 171)
        self.login_widget = QtWidgets.QWidget(parent=MainWindow)
        self.login_widget.setObjectName("login_widget")
        self.name_input = QtWidgets.QLineEdit(parent=self.login_widget)
        self.name_input.setGeometry(QtCore.QRect(120, 70, 113, 20))
        self.name_input.setInputMask("")
        self.name_input.setText("")
        self.name_input.setObjectName("name_input")
        self.name = QtWidgets.QLabel(parent=self.login_widget)
        self.name.setGeometry(QtCore.QRect(60, 70, 54, 16))
        self.name.setObjectName("name")
        self.title = QtWidgets.QLabel(parent=self.login_widget)
        self.title.setGeometry(QtCore.QRect(150, 30, 61, 31))
        self.title.setObjectName("title")
        self.start_button = QtWidgets.QPushButton(parent=self.login_widget)
        self.start_button.setGeometry(QtCore.QRect(140, 100, 75, 24))
        self.start_button.setObjectName("start_button")
        MainWindow.setCentralWidget(self.login_widget)

        self.retranslateUi_login(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi_login(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "网络聊天室"))
        self.name.setText(_translate("MainWindow", "用户名"))
        self.title.setText(_translate("MainWindow", "网络聊天室"))
        self.start_button.setText(_translate("MainWindow", "登入"))
