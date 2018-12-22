#Reference to main code
import sys

from PyQt5.QtWidgets import QTableWidgetItem

sys.path.append(sys.path[0] + "/../..")
from main import main as base_main

#using interface
from PyQt5 import QtWidgets, QtCore
import design

data = dict()
#json file interaction
import json

def get_settings_from_file():
    try:
        file = open("input.txt")
    except IOError as e:
        update_settings_file()
    else:
        with file:
            data = json.load(file)

def update_settings_file():
    with open("config_file.json","w") as write_file:
        json.dump(data, write_file)




class GUI_handler(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):

        super().__init__()
        self.setupUi(self)
        self.SyncButton.clicked.connect(base_main)

        get_settings_from_file()
        self.SettingsButton.clicked.connect(update_settings_file)


        self.create_table()
        self.tableWidget.itemChanged.connect(self.check_empty)
        self.AddButton.clicked.connect(self.create_raw)


    def create_raw(self):
        table = self.tableWidget
        rows = table.rowCount()
        table.insertRow(rows + 1)
        table.setItem(0, 0, QTableWidgetItem(""))
        table.setItem(rows, 1, QTableWidgetItem(""))
        table.setCurrentCell(0,0)



    def create_table(self):
        table = self.tableWidget
        table.setColumnCount(2)
        table.setRowCount(10)
        table.setHorizontalHeaderLabels(["Доска", "Календарь"])


    def check_empty(self):
        table = self.tableWidget
        item = table.findItems("", QtCore.Qt.MatchExactly)
        if len(item) != 0 and not item[0].isSelected():
            table.removeRow(table.row(item[0]))


def main():

    app = QtWidgets.QApplication(sys.argv)

    window = GUI_handler()
    window.show()
    app.exec()

if __name__ == '__main__':
    main()