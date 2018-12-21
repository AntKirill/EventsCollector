import sys
sys.path.append(sys.path[0] + "/../..")
from main import main as base_main

from PyQt5 import QtWidgets

import design



class GUI_handler(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        #base_main()



def main():

    app = QtWidgets.QApplication(sys.argv)
    window = GUI_handler()
    window.show()
    app.exec()

if __name__ == '__main__':
    main()