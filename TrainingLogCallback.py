
import tensorflow.keras

class TrainingCallback(tensorflow.keras.callbacks.Callback):

    def __init__(self, epochProgressBar, batchesProgressBar, lossLabel, accLabel):
        super(TrainingCallback, self).__init__()
        self.epochProgressBar = epochProgressBar
        self.batchesProgressBar = batchesProgressBar
        self.lossLabel = lossLabel
        self.accLabel = accLabel


    # This function is called when the training begins
    def on_train_begin(self, logs={}):
        # Initialize the lists for holding the logs, losses and accuracies
        self.losses = []
        self.acc = []
        self.logs = []
        self.total_epochs = self.params['epochs']
        self.total_batches = self.params['steps']

    def on_epoch_begin(self, epoch, logs=None):
        self.batchesProgressBar.setValue(0)

    def on_batch_end(self, batch, logs=None):
        progress = ((batch+1)/self.total_batches)*100
        self.batchesProgressBar.setValue(progress)
        self.lossLabel.setText("Loss = "+str(logs.get('loss')))
        self.accLabel.setText("Acc = " + str(logs.get('accuracy')))


    # This function is called at the end of each epoch
    def on_epoch_end(self, epoch, logs={}):

        # Append the logs, losses and accuracies to the lists
        self.logs.append(logs)
        self.losses.append(logs.get('loss'))
        self.acc.append(logs.get('accuracy'))

        progress = ((epoch+1)/self.total_epochs) * 100
        self.epochProgressBar.setValue(progress)


class PredictCallback(tensorflow.keras.callbacks.Callback):

    def __init__(self, predictionProgressBar):
        super(PredictCallback, self).__init__()
        self.predictionProgressBar = predictionProgressBar

    def on_predict_begin(self, logs=None):
        self.total_batches = self.params['steps']

    def on_predict_batch_end(self, batch, logs=None):
        progress = ((batch + 1) / self.total_batches) * 100
        self.predictionProgressBar.setValue(progress)