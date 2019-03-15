import datetime
import sqlite3

import numpy as np
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import LSTM, Dense, Flatten, TimeDistributed
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


def get_dataset(db_path, station="KTOL", obs="temp"):
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    query = "select * from {} order by datetime desc".format(station)
    raw_data = list(cur.execute(query))

    obs_col = obs_to_col[obs]
    datetimes = np.array([datetime.datetime.strptime(
        row[0], "%Y-%m-%d %H:%M:%S") for row in raw_data])
    data = np.array([row[obs_col] for row in raw_data])

    return datetimes, data


def format_dataset(data_stream, num_terms=4):
    X = np.array([data_stream[i:i+num_terms]
                  for i in range(len(data_stream)-num_terms)])
    X = X.reshape((X.shape[0], 2, 2, 1))
    y = np.array([data_stream[i+num_terms]
                  for i in range(len(data_stream)-num_terms)])
    return X, y


def get_model(input_dim, activation='relu', optimizer='adam', loss='mse'):
    print("Creating the model...")
    model = Sequential()
    model.add(TimeDistributed(Conv1D(filters=64, kernel_size=1,
                                     activation=activation), input_shape=(None, 2, 1)))
    model.add(TimeDistributed(MaxPooling1D(pool_size=2)))
    model.add(TimeDistributed(Flatten()))
    model.add(LSTM(50, activation=activation))
    model.add(Dense(1))
    model.compile(optimizer=optimizer, loss=loss)
    return model


def fit_model(model, X, y, epochs):
    print("Training the model...")
    model.fit(X, y, epochs=epochs, verbose=0)
    print("Model training finished!")
    return model


def predict(model, X):
    pred = []
    for arr in X:
        arr = arr.reshape((1, 2, 2, 1))
        pred.append(model.predict(arr)[0][0])
    return pred


if __name__ == '__main__':
    DB_PATH = 'observations.db'
    STATION = 'KTOL'
    TERMS = 4
    EPOCHS = 5000

    datetimes, data = get_dataset(DB_PATH)
    X, y = format_dataset(data, TERMS)
    model = get_model(TERMS)
    model = fit_model(model, X, y, EPOCHS)

    pred = predict(model, X)

#    for i in range(len(pred)):
#        prediction = model.predict(X[i].reshape((1, X[i].shape[0])))[0][0]
#        actual = y[i]
#        print(f"PREDICTION: {prediction:.2f} --> ACTUAL: {actual}")

    plt.plot(datetimes[TERMS:], y, 'k', label='ACTUAL')
    plt.plot(datetimes[TERMS:], pred, 'y', label='PREDICTED')
    plt.legend()
    plt.show()
