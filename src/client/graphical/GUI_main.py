# Reference to main code
import sys

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QTableWidgetItem

import src.client.graphical.design as design
from main import main as base_main
from src.config.config_handler import Config_Handler


# sys.path.append(sys.path[0] + "/../..")
#
# sys.path.append(sys.path[0] + "/../../config")

# using interface


class GUI_handler(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.CH = Config_Handler()
        self.settings = self.CH.get_settings_map()
        self.set_config_data()

        self.SettingsButton.clicked.connect(self.update_qconfig_data)

        self.SyncButton.clicked.connect(base_main)

        self.create_table()
        self.tableWidget.itemChanged.connect(self.check_empty)
        self.AddButton.clicked.connect(self.create_raw)

    def set_config_data(self):
        self.DeleteEventsRadio.setChecked(self.settings['delete_expired'])
        self.DeleteTimeRadio.setChecked(self.settings['data_only'])
        self.EventNames.setText(self.settings['event_names'])

    def update_config_data(self):
        to_config = {
            'delete_expired': self.DeleteEventsRadio.isChecked(),
            'data_only': self.DeleteTimeRadio.isChecked(),
            'event_names': str(self.EventNames.text())
        }
        self.CH.update_settings_map(to_config)

    def create_raw(self):
        table = self.tableWidget
        rows = table.rowCount()
        table.insertRow(rows + 1)
        table.setItem(0, 0, QTableWidgetItem(""))
        table.setItem(rows, 1, QTableWidgetItem(""))
        table.setCurrentCell(0, 0)

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
