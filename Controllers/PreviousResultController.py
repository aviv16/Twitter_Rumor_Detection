import csv

from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem

from UI.viewPreviousEvents import Ui_ViewPreviousEvent


class PreviousResultController(QMainWindow):
    def __init__(self, parent=None):
        super(PreviousResultController, self).__init__(parent)
        self.ui = Ui_ViewPreviousEvent()
        self.ui.setupUi(self)

        # connect listeners
        self.ui.backBtn.clicked.connect(self.backToMain)

        self.constructTable()

    # construct the table with the information about previous classifications
    def constructTable(self):
        row_num = 0
        with open('Previous_Classification.txt') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            num_of_cols = 4
            self.ui.tableView.setColumnCount(num_of_cols)
            self.ui.tableView.setColumnWidth(0, 150)
            self.ui.tableView.setColumnWidth(1, 150)
            self.ui.tableView.setColumnWidth(2, 100)
            self.ui.tableView.setColumnWidth(3, 110)
            self.ui.tableView.setHorizontalHeaderLabels(['Name', 'Probability to be a Rumor', 'Classification', 'Date'])
            previous_events_list = []
            for row in csv_reader:
                # update rows number
                self.ui.tableView.setRowCount(row_num+1)
                previous_events_list.append(row)
            for row in reversed(previous_events_list):
                # update rows number
                self.ui.tableView.setRowCount(row_num+1)
                for i in range(num_of_cols):
                    item = QTableWidgetItem(row[i])
                    item.setTextAlignment(132)
                    self.ui.tableView.setItem(row_num, i, item)
                row_num += 1
        self.ui.tableView.show()

    # go back to the main window
    def backToMain(self):
        # Code to replace the main window with a new window
        from Controllers.MainWindowController import MainWindowController
        self.close()
        self.MyMainWindow = MainWindowController()
        self.MyMainWindow.show()
