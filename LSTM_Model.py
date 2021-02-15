# LSTM with dropout for sequence classification in the IMDB dataset
import numpy as np
from keras.datasets import imdb
from keras.preprocessing import sequence
import tensorflow.keras
from sklearn.model_selection import train_test_split

from attention import Attention
from Preprocessing import getData, N

def train():
    # fix random seed for reproducibility
    #np.random.seed(7)
    # load the dataset but only keep the top n words, zero the rest
    #top_words = 5000
    #(X_train, y_train), (X_test, y_test) = imdb.load_data(num_words=top_words)
    x, y = getData()
    _x_train, _x_test, _y_train, _y_test = train_test_split(x, y, test_size = 0.03, train_size=0.07, random_state = 42)
    K = len(_x_train[0][0])
    #tf.convert_to_tensor(_x_train)
    #tf.convert_to_tensor(_y_train)
    #_y_train = np.array(_y_train)
    #_x_train = np.vstack(_x_train)

    #print("x shape: ",_x_train.shape)
    #print("y shape: ",_y_train.shape)
    # _x_train.reshape(56,100,66)
    # truncate and pad input sequences
    max_review_length = 500
    #X_train = sequence.pad_sequences(X_train, maxlen=max_review_length)
    #X_test = sequence.pad_sequences(X_test, maxlen=max_review_length)
    # create the model
    embedding_vecor_length = 32
    model = tensorflow.keras.Sequential()
    #model.add(tensorflow.keras.layers.Embedding(top_words, embedding_vecor_length, input_length=max_review_length))
    #model.add(tensorflow.keras.layers.LSTM(1024, dropout=0.3, recurrent_dropout=0.2, return_sequences=True))
    model.add(tensorflow.keras.layers.LSTM(128, dropout=0.3, recurrent_dropout=0.2,input_shape=(N, K), return_sequences=True))
    model.add(tensorflow.keras.layers.LSTM(128, dropout=0.3, recurrent_dropout=0.2,input_shape=(N, K), return_sequences=True))
    model.add(Attention(name='attention_weight'))
    model.add(tensorflow.keras.layers.Dense(1, activation='sigmoid'))

    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    print(model.summary())
    print(_x_train.shape)
    model.fit(_x_train, _y_train, epochs=3, batch_size=64)
    #model.fit(X_train, y_train, epochs=3, batch_size=64)
    # Final evaluation of the model
    scores = model.evaluate(_x_test, _y_test, verbose=0)
    print("Accuracy: %.2f%%" % (scores[1]*100))
    model.save("D:\Desktop\לימודים אורי\סמסטר 8\פרויקט גמר חלק ב\Project_B\model")


train()
