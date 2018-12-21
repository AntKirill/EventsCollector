from PyQt5 import QtWidgets
import design

class GUI_handler(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
