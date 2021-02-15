import ctypes
from datetime import datetime

import tensorflow
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QMainWindow
from sklearn.model_selection import train_test_split

from Preprocessing import PreprocessingHelper, N, K
from TrainingLogCallback import TrainingCallback
from UI.newModelWindow import Ui_NewModelWindow
from attention import attention


class NewModelController(QMainWindow):
    def __init__(self, parent=None):
        super(NewModelController, self).__init__(parent)
        self.ui = Ui_NewModelWindow()
        self.ui.setupUi(self)

        self.test_size = 0.3

        self.preprocessor = PreprocessingHelper()

        # connect listeners
        self.ui.browseBtn.clicked.connect(self.browseFile)
        self.ui.trainBtn.clicked.connect(self.train)
        self.ui.backBtn.clicked.connect(self.backToMain)
        self.ui.trainingSlider.valueChanged[int].connect(self.trainingValueChange)

    # Follow the changes in the slider and update the values accordingly
    def trainingValueChange(self):
        train_val = self.ui.trainingSlider.value()
        if train_val == 0:
            train_val = 1
        test_val = 100 - train_val
        self.test_size = test_val/100
        self.ui.trainingLabel.setText(str(train_val) + "%")
        self.ui.testingLabel.setText(str(test_val) + "%")

    # browse a file to the dataset
    def browseFile(self):
        data_path, _ = QtWidgets.QFileDialog.getOpenFileName(None, 'Open File', r"datasets\\", '*.xls')
        self.ui.datasetFileTxt.setText(data_path)

    # train a model using the entered values
    def train(self):
        self.model_name = self.ui.modelNameTxt.text()
        now = datetime.now()  # current date and time

        # check validity of the values
        if not self.model_name.isalnum():
            self.ui.errorLabel.setText("Model name must be letters and numbers only!")
            return
        date_time = now.strftime("%d_%m_%Y_%H_%M")
        self.model_name = self.model_name + "_" + date_time + ".h5"
        self.dataset_file_name = self.ui.datasetFileTxt.text()
        if not (self.dataset_file_name.endswith(".xls") or self.dataset_file_name.endswith(".xlsx")):
            self.ui.errorLabel.setText("Invalid dataset file")
            return
        if not self.ui.epochsTxt.text().isnumeric():
            self.ui.errorLabel.setText("Invalid epoch number")
            return
        if not self.ui.batchSizeTxt.text().isnumeric():
            self.ui.errorLabel.setText("Invalid batch size")
            return

        # prepare screen to show training progress
        self.ui.topAreaBlock.setHidden(False)
        self.ui.mdiArea.setHidden(True)
        self.ui.errorLabel.setText("")
        self.ui.batchProgressBar.setValue(0)
        self.ui.epochProgressBar.setValue(0)
        self.ui.backBtn.setVisible(False)

        # create a thread to execute the training process to avoid screen freeze
        callback = TrainingCallback(self.ui.epochProgressBar, self.ui.batchProgressBar, self.ui.lossLabel, self.ui.accLabel)
        self.t = TrainingThread(int(self.ui.epochsTxt.text()),int(self.ui.batchSizeTxt.text()),self.dataset_file_name,self.ui.preprocessProgressBar,callback,self.test_size,self.model_name, self.preprocessor)
        self.t.finished.connect(self.backToMain)
        self.t.start()

    # go back to the main window
    def backToMain(self):
        # Code to replace the main window with a new window
        from Controllers.MainWindowController import MainWindowController
        self.close()
        self.MyMainWindow = MainWindowController()
        #self.MainWindowui = Ui_MainWindow()
        #self.MainWindowui.setupUi(self.MyMainWindow)
        self.MyMainWindow.show()

# thread to execute the training
class TrainingThread(QThread):
    def __init__(self, num_of_epochs,batch_size,dataset_file_name,preprocessProgressBar,callback,test_size,model_name,preproccessor, parent=None):
        QThread.__init__(self, parent)
        self.num_of_epochs = num_of_epochs
        self.batch_size = batch_size
        self.dataset_file_name = dataset_file_name
        self.preprocessProgressBar = preprocessProgressBar
        self.callback = callback
        self.test_size = test_size
        self.model_name = model_name
        self.preproccessor = preproccessor
        self.error = None

    def is_success(self):
        return self.error is None

    def run(self):
        x, y = self.preproccessor.getData(self.dataset_file_name, self.preprocessProgressBar)
        _x_train, _x_test, _y_train, _y_test = train_test_split(x, y, test_size=self.test_size, random_state=42)
        model = tensorflow.keras.Sequential()
        model.add(tensorflow.keras.layers.LSTM(128, dropout=0.3, recurrent_dropout=0.2, input_shape=(N, K),
                                               return_sequences=True))
        model.add(tensorflow.keras.layers.LSTM(128, dropout=0.3, recurrent_dropout=0.2, input_shape=(N, K),
                                               return_sequences=True))
        model.add(attention(name='attention_weight'))
        model.add(tensorflow.keras.layers.Dense(1, activation='sigmoid'))
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        print(model.summary())
        print(_x_train.shape)
        model.fit(_x_train, _y_train, epochs=self.num_of_epochs, batch_size=self.batch_size, callbacks=[self.callback])
        # Final evaluation of the model
        scores = model.evaluate(_x_test, _y_test, verbose=0)
        # test = model.predict_classes(_x_test)
        print("Accuracy: %.2f%%" % (scores[1] * 100))
        saveModel = ctypes.windll.user32.MessageBoxW(0, "The accuracy of the model is: " + str(scores[1] * 100) +
                                                        "%.\nDo you want to save it?", "Save Model?", 1)
        if saveModel == 1:
            model.save("Models\\" + self.model_name)
            ctypes.windll.user32.MessageBoxW(0, self.model_name + " saved successfully", "Model Saved", 0)
