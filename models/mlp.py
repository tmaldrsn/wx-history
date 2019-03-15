import datetime
import sqlite3

import numpy as np
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Dense

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

    return np.flip(datetimes), np.flip(data)


def format_dataset(data_stream, num_terms):
    X = np.array([data_stream[i:i+num_terms]
                  for i in range(len(data_stream)-num_terms)])
    y = np.array([data_stream[i+num_terms]
                  for i in range(len(data_stream)-num_terms)])
    return X, y


def get_model(input_dim, activation='relu', optimizer='adam', loss='mse'):
    print("Creating the model...")
    model = Sequential()
    model.add(Dense(100, activation=activation, input_dim=input_dim))
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
        arr = arr.reshape((1, arr.shape[0]))
        pred.append(model.predict(arr)[0][0])
    return np.array(pred)


def get_future_data(data, epochs, num_terms, num_future_terms):
    X, y = format_dataset(data, num_terms)
    model = get_model(input_dim=num_terms)
    model = fit_model(model, X, y, epochs=epochs)
    arr = X[-1]
    print(arr, arr.shape)
    future_terms = []
    for _ in range(num_future_terms):
        arr = arr.reshape((1, arr.shape[0]))
        next_term = model.predict(arr).item(0)
        arr = np.append(arr.flatten()[1:], next_term)
        future_terms.append(next_term)
    return future_terms


def plot_predictions(data):
    plt.plot(range(len(data)), data, 'k', label='Historical')
    for len_history, color in zip([12, 24, 36, 48], ['r', 'b', 'g', 'y']):
        future_terms = get_future_data(
            data, epochs=2000, num_terms=len_history, num_future_terms=100)
        plt.plot(range(len(data), len(data)+len(future_terms)),
                 future_terms, color, label=f"{len_history} hours")
    plt.legend()
    plt.show()


if __name__ == '__main__':
    DB_PATH = 'observations.db'
    STATION = 'KTOL'
    TERMS = 5
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
