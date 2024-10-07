from PyQt6 import QtCore, QtGui, QtWidgets
import subprocess

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(482, 364)
        MainWindow.setMinimumSize(QtCore.QSize(482, 364))
        MainWindow.setMaximumSize(QtCore.QSize(482, 364))
        MainWindow.setAccessibleName("")
        MainWindow.setUnifiedTitleAndToolBarOnMac(False)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(parent=self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 481, 341))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lineEdit = QtWidgets.QLineEdit(parent=self.verticalLayoutWidget)
        self.lineEdit.setText("")
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.pushButton = QtWidgets.QPushButton(parent=self.verticalLayoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.open_file_dialog)
        self.horizontalLayout.addWidget(self.pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(parent=self.verticalLayoutWidget)
        self.label.setTextFormat(QtCore.Qt.TextFormat.PlainText)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.lineEdit_2 = QtWidgets.QLineEdit(parent=self.verticalLayoutWidget)
        self.lineEdit_2.setText("")
        self.lineEdit_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.horizontalLayout_2.addWidget(self.lineEdit_2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.pushButton_2 = QtWidgets.QPushButton(parent=self.verticalLayoutWidget)
        self.pushButton_2.setAutoFillBackground(False)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.convert)
        self.verticalLayout.addWidget(self.pushButton_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "PDF to PNG Converter - by aybrky"))
        self.lineEdit.setPlaceholderText(_translate("MainWindow", "Enter file path"))
        self.pushButton.setText(_translate("MainWindow", "Browse"))
        self.label.setText(_translate("MainWindow", "Examples:\n"
                                                                     "   •  all\n"
                                                                     "   •  5\n"
                                                                     "   •  1-8\n"
                                                                     "   •  7,8,11,19,56"))
        self.lineEdit_2.setPlaceholderText(_translate("MainWindow", "Enter pages"))
        self.pushButton_2.setText(_translate("MainWindow", "Convert"))


    def open_file_dialog(self):
        file_filter = "PDF Files (*.pdf)"
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Open PDF File", "", file_filter)

        if file_name:
            self.lineEdit.setText(file_name)

    def convert(self):
        output_result = self.run_subprocess(f"python ../main.py --path {self.lineEdit.text()} --input {self.lineEdit_2.text()}")
        print(output_result)
    def run_subprocess(self, command):
        try:
            result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)

            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Hata: {e.stderr}"

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
