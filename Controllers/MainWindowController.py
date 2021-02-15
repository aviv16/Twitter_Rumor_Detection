from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow

from Controllers.ClassifyEventController import ClassifyEventController
from Controllers.PreviousResultController import PreviousResultController
from Controllers.newModelController import NewModelController
from UI.mainWindow import Ui_MainWindow


class MainWindowController(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindowController, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # connect listeners
        self.ui.newModelBtn.clicked.connect(self.createNewModel)
        self.ui.classifyEventBtn.clicked.connect(self.classifyEvent)
        self.ui.exitBtn.clicked.connect(self.exitApplication)
        self.ui.prevResultsBtn.clicked.connect(self.showPrevClassifications)

    # Go to new model window
    def createNewModel(self):
        self.close()
        self.MyMainWindow = NewModelController()
        self.MyMainWindow.show()

    # Go to classify new event window
    def classifyEvent(self):
        self.close()
        self.MyMainWindow = ClassifyEventController()
        self.MyMainWindow.show()

    # Go to view previous classification window
    def showPrevClassifications(self):
        self.close()
        self.MyMainWindow = PreviousResultController()
        self.MyMainWindow.show()

    def exitApplication(self):
        import sys
        self.close()
        sys.exit(0)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MainWindowController()
    MainWindow.show()
    sys.exit(app.exec_())
