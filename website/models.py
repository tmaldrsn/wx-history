import datetime
import sqlite3

import numpy as np
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Dense, Flatten, LSTM, RepeatVector, TimeDistributed
from keras.layers.convolutional import Conv1D, MaxPooling1D

obs_to_col = {
    "vis": 2,
    "temp": 5,
    "dp": 6,
    "hum": 9,
    "wc": 10,
    "hi": 11,
    "alt": 12,
    "sea": 13,
    "precip": 14
}

DB_PATH = 'observations.db'
STATION = 'KTOL'
OBS = 'temp'


def get_dataset(db_path=DB_PATH, station=STATION, obs=OBS):
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    query = "select * from {} order by datetime desc".format(station)
    raw_data = list(cur.execute(query))

    obs_col = obs_to_col[obs]
    datetimes = np.array([datetime.datetime.strptime(
        row[0], "%Y-%m-%d %H:%M:%S") for row in raw_data])
    data = np.array([row[obs_col] for row in raw_data])

    return np.flip(datetimes), np.flip(data)


def format_dataset(data_stream, num_terms, model='mlp'):
    X = np.array([data_stream[i:i+num_terms]
                  for i in range(len(data_stream)-num_terms)])
    y = np.array([data_stream[i+num_terms]
                  for i in range(len(data_stream)-num_terms)])

    if model == 'mlp':
        pass
    elif model == 'cnn' or model == 'lstm':
        X = X.reshape((X.shape[0], X.shape[1], 1))
    elif model == 'hybrid':
        if num_terms in [i**2 for i in range(100)]:
            X = X.reshape(
                (X.shape[0], int(np.sqrt(num_terms)), int(np.sqrt(num_terms)), 1))
        else:
            raise Exception(
                "The dataset won't work in training a CNN, since the number of terms is not a perfect square.")
    return X, y


class NeuralNetwork():
    def __init__(self, input_dim=3, activation='relu', optimizer='adam', loss='mse'):
        self.input_dim = input_dim
        self.activation = activation
        self.optimizer = optimizer
        self.loss = loss
        self.id = ''
        self.model = Sequential()

    def fit(self, X, y, epochs):
        self.model.fit(X, y, epochs=epochs, verbose=0)
        # return self.model.fit(X, y, epochs=epochs, verbose=0)

    def predict(self, x_input):
        return self.model.predict(x_input)

    def get_future_data(self, data, epochs=3000, num_future_terms=100):
        X, y = format_dataset(data, self.input_dim, self.id)
        self.fit(X, y, epochs=epochs)

        future_terms = []
        arr = X[-1]
        for _ in range(num_future_terms):
            #arr = arr.reshape((1, arr.shape[0]))
            if self.id == "mlp":
                arr = arr.reshape((1, arr.shape[0]))
            elif self.id == "cnn":
                arr = arr.reshape((1, arr.shape[0], 1))
            elif self.id == "lstm":
                arr = arr.reshape((1, arr.shape[0], 1))
            elif self.id == "hybrid":
                arr = arr.reshape((1, 2, 2, 1))
            elif self.id == "autoencoder":
                arr = arr.reshape((1, arr.shape[0], 1))
            next_term = self.predict(arr).item(0)
            arr = np.append(arr.flatten()[1:], next_term)
            future_terms.append(next_term)
        return np.array(future_terms)

    def plot_predictions(self, data):
        future_terms = self.get_future_data(data)

        plt.plot(range(len(data)), data, 'k', label='Historical')
        plt.plot(range(len(data), len(data)+len(future_terms)),
                 future_terms, 'r', label="Prediction")
        plt.axvline(x=len(data))
        plt.legend()
        plt.show()


class MultiLayerPerceptron(NeuralNetwork):
    def __init__(self, input_dim=3, activation='relu', optimizer='adam', loss='mse'):
        super().__init__(input_dim, activation, optimizer, loss)
        self.id = 'mlp'
        self.get_model()

    def get_model(self):
        self.model = Sequential()
        self.model.add(Dense(100, activation=self.activation,
                             input_dim=self.input_dim))
        self.model.add(Dense(1))
        self.model.compile(optimizer=self.optimizer, loss=self.loss)


class ConvolutionalNeuralNetwork(NeuralNetwork):
    def __init__(self, input_dim=3, activation='relu', optimizer='adam', loss='mse'):
        super().__init__(input_dim, activation, optimizer, loss)
        self.id = 'cnn'
        self.get_model()

    def get_model(self):
        self.model = Sequential()
        self.model.add(Conv1D(filters=64, kernel_size=2,
                              activation=self.activation, input_shape=(self.input_dim, 1)))
        self.model.add(MaxPooling1D(pool_size=2))
        self.model.add(Flatten())
        self.model.add(Dense(50, activation=self.activation))
        self.model.add(Dense(1))
        self.model.compile(optimizer=self.optimizer, loss=self.loss)


class LongShortTermMemory(NeuralNetwork):
    def __init__(self, input_dim=3, activation='relu', optimizer='adam', loss='mse'):
        super().__init__(input_dim, activation, optimizer, loss)
        self.id = 'lstm'
        self.get_model()

    def get_model(self):
        self.model = Sequential()
        self.model.add(LSTM(50, activation=self.activation,
                            input_shape=(self.input_dim, 1)))
        self.model.add(Dense(1))
        self.model.compile(optimizer=self.optimizer, loss=self.loss)


class Hybrid(NeuralNetwork):
    def __init__(self, input_dim=16, activation='relu', optimizer='adam', loss='mse'):
        super().__init__(input_dim, activation, optimizer, loss)
        self.id = 'hybrid'
        self.get_model()

    def get_model(self):
        self.model = Sequential()
        self.model.add(TimeDistributed(Conv1D(filters=64, kernel_size=1,
                                              activation=self.activation), input_shape=(None, 2, 1)))
        self.model.add(TimeDistributed(MaxPooling1D(pool_size=2)))
        self.model.add(TimeDistributed(Flatten()))
        self.model.add(LSTM(50, activation=self.activation))
        self.model.add(Dense(1))
        self.model.compile(optimizer=self.optimizer, loss=self.loss)


class Autoencoder(NeuralNetwork):
    def __init__(self, input_dim=3, activation='relu', optimizer='adam', loss='mse'):
        super().__init__(input_dim, activation, optimizer, loss)
        self.id = 'autoencoder'
        self.get_model()

    def get_model(self):
        self.model = Sequential()
        self.model.add(LSTM(100, activation=self.activation,
                            input_shape=(self.input_dim, 1)))
        self.model.add(RepeatVector(2))
        self.model.add(
            LSTM(100, activation=self.activation, return_sequences=True))
        self.model.add(TimeDistributed(Dense(1)))
        self.model.compile(optimizer=self.optimizer, loss=self.loss)
