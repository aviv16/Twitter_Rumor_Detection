import ctypes
from datetime import datetime

import xlrd
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QMainWindow
from tensorflow.keras.models import load_model

from Preprocessing import PreprocessingHelper, N
from TrainingLogCallback import PredictCallback
from UI.loadEventWindow import Ui_LoadEventWindow
from attention import attention


class ClassifyEventController(QMainWindow):
    def __init__(self, parent=None):
        super(ClassifyEventController, self).__init__(parent)
        self.ui = Ui_LoadEventWindow()
        self.ui.setupUi(self)

        # connect listeners
        self.ui.backBtn.clicked.connect(self.backToMain)
        self.ui.browseEventBtn.clicked.connect(self.browseEventFile)
        self.ui.newModelBtn.clicked.connect(self.createNewModel)
        self.ui.browseModelBtn.clicked.connect(self.browseModelFile)
        self.ui.classifyEventBtn.clicked.connect(self.classifyEvent)
        self.ui.previousClassificationBtn.clicked.connect(self.viewPrevClassifications)

    # go back to the main window
    def backToMain(self):
        from Controllers.MainWindowController import MainWindowController
        self.close()
        self.MyMainWindow = MainWindowController()
        self.MyMainWindow.show()

    # go to create new model window
    def createNewModel(self):
        from Controllers.newModelController import NewModelController
        self.close()
        self.MyMainWindow = NewModelController()
        self.MyMainWindow.show()

    # go to see previous classifications window
    def viewPrevClassifications(self):
        from Controllers.PreviousResultController import PreviousResultController
        self.close()
        self.MyMainWindow = PreviousResultController()
        self.MyMainWindow.show()

    # browse an event file
    def browseEventFile(self):
        data_path, _ = QtWidgets.QFileDialog.getOpenFileName(None, 'Open File', r"events\\", '*.xls')
        self.ui.eventFilePathText.setText(data_path)

    # browse a model (.h5) file
    def browseModelFile(self):
        data_path, _ = QtWidgets.QFileDialog.getOpenFileName(None, 'Open File', r"Models\\", '*.h5')
        self.ui.ModelFilePathText.setText(data_path)

    # classify an event to rumor or not-rumor
    def classifyEvent(self):
        # check validity of the values
        if self.ui.eventNameText.text() == "" or self.ui.eventNameText.text().find(",") != -1:
            self.ui.errorLabel.setText("Invalid event name")
            return
        if not self.ui.eventFilePathText.text().endswith(".xls"):
            self.ui.errorLabel.setText("Choose a valid event file")
            return
        if self.ui.ModelFilePathText.text() == "" or not self.ui.ModelFilePathText.text().endswith(".h5"):
            self.ui.errorLabel.setText("Choose a valid model file")
            return


        # prepare screen to show classification progress
        self.ui.errorLabel.setText("")
        self.ui.topBlock.setHidden(False)
        self.ui.bottomBlock.setHidden(False)
        self.ui.middleBlock.setHidden(True)
        self.ui.predictProgressBar.setValue(0)

        # create a thread to execute the classification process to avoid screen freeze
        callback = PredictCallback(self.ui.predictProgressBar)
        self.t = PredictThread(self.ui.eventFilePathText.text(),self.ui.ModelFilePathText.text(),callback,self.ui.eventNameText.text(),self.ui.predictProgressBar)
        self.t.finished.connect(self.organizeWindow)
        self.t.start()

    # clean window after classification finished
    def organizeWindow(self):
        self.ui.topBlock.setHidden(True)
        self.ui.middleBlock.setHidden(False)
        self.ui.bottomBlock.setHidden(True)
        self.ui.eventNameText.setText("")
        self.ui.eventFilePathText.setText("")
        self.ui.ModelFilePathText.setText("")

# thread to execute the classification
class PredictThread(QThread):
    def __init__(self, eventFilePathText, ModelFilePathText, callback, eventNameText, progressBar, parent=None):
        QThread.__init__(self, parent)
        self.eventFilePathText = eventFilePathText
        self.ModelFilePathText = ModelFilePathText
        self.callback = callback
        self.eventNameText = eventNameText
        self.progressBar = progressBar
        self.preprocessor = PreprocessingHelper()
        self.error = None

    def is_success(self):
        return self.error is None

    def run(self):
        file = xlrd.open_workbook(self.eventFilePathText)
        sheet = file.sheet_by_index(0)
        total_cols = sheet.ncols
        total_rows = sheet.nrows
        col = 0
        row = 0
        new_event = []
        self.progressBar.setValue(5)
        while row < total_rows and sheet.cell_value(row,0) != "":
            while col < total_cols and sheet.cell_value(row, col) != "":
                new_event.append(sheet.cell_value(row, col))
                col = col + 1
            col = 0
            row = row + 1
        new_event_len = len(new_event)
        self.progressBar.setValue(16)
        data, classification, event_ids = self.preprocessor.splitFileToEvents("datasets\\DatasetForClassification.xls")
        data.append(new_event)
        all_posts, padded_posts_to_event_count = self.preprocessor.getAllEvents(data)
        self.progressBar.setValue(35)
        total_tf_idf = self.preprocessor.calculateTFIDF(all_posts)
        new_event_tfidf = total_tf_idf[len(all_posts) - len(new_event):]
        post_series = self.preprocessor.createPostSeries(new_event_tfidf)
        post_series = post_series[:new_event_len // N + 1]
        file = self.ModelFilePathText
        self.progressBar.setValue(51)
        model = load_model(file, custom_objects={'attention': attention})
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        self.progressBar.setValue(62)
        prediction_probability = model.predict(post_series, steps=len(post_series), callbacks=[self.callback])

        avg_prob = sum(prediction_probability) / len(prediction_probability)
        if avg_prob < 0.5:
            pred = "non-rumor"
            classif = 0
        else:
            pred = "rumor"
            classif = 1
        # append results to classification file
        rounded_prob = round(avg_prob[0], 2)
        with open("Previous_Classification.txt", "a") as res_file:
            res_file.write(
                self.eventNameText + "," + str(avg_prob) + "," + str(classif) + "," + datetime.now().strftime(
                    "%d/%m/%Y") + "\n")
        ctypes.windll.user32.MessageBoxW(0, "The event is classified as " + pred + "\n(probability of being a rumor: "+str(rounded_prob)+")", "Event Classified", 0)
