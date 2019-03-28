# Collecting data from NOAA based on a given station's ID

Basic web backend exercise covering the following topics:

* databases (sqlite3)
* web scraping (beautifulsoup)
* basic webdev (flask, jinja2)
* restful api & http requests w/ flask & jquery
* machine learning (keras)

To run the project, execute ```python3 run.py```

## ABOUT THE PROJECT

NOAA provides 3-day histories of observations for over 2000 weather stations, and updates them every 20 minutes or hour depending on the station. However, there is no easily findable resource containing similar hourly histories online. The goal of this project is to collect the given observation data and compile them into a database containing historical hourly data around the country for much longer than 3 days. It also serves as a basic data collection exercise, along with a unique opportunity to explore weather trends in the country over time as the database becomes more complete.

## COMMAND LINE TOOLS

Currently the one of the only main tools used in the command line is ```python3 website/observations.py``` which simply updates the database. See "DATA MAINTENANCE" below.
There are predictive models written using the Keras library also available in the repository in ```website/models.py``` or individually in the ```models/``` directory including:
    1. Multilayer Perceptron
    2. Convolutional Neural Network
    3. Long Short-Term Memory (LSTM) Networks
    4. Hybrid CNN/LSTM Network
    5. Autoencoder
There are plotting capabilities, however they only currently work for the first three options. More documentation will be available in the future for these features as they are developed.

## DATA FORMAT

For each observation, there is a 17-tuple of data, some of which are null, describing the weather at the particular point in time. Some stations collect data every 20 minutes, while most other stations record data every hour. The format of the data in the database goes as follows.

In the master database (observations.db), there is a stations table containing information about each particular station:

| ID   | STATE | STATION NAME                                | LATITUDE | LONGITUDE |
|------|-------|---------------------------------------------|----------|-----------|
| K79J | AL    | Andalusia, Andalusia-Opp Municipal Airport  | 31.3     | -86.3833  |
| KANB | AL    | Anniston Metro Airport                      | 33.5904  | -85.8479  |
| KAUO | AL    | Auburn-Opelika Airport                      | 32.6167  | -85.4333  |
| KBFM | AL    | Mobile, Mobile Downtown Airport             | 30.6139  | -88.0633  |
| KBHM | AL    | Birmingham, Birmingham International Airport| 33.5656  | -86.745   |
| KDCU | AL    | Decatur, Pryor Field                        | 34.6581  | -86.9433  |
| KDHN | AL    | Dothan, Dothan Regional Airport             | 31.3214  | -85.4497  |
| KEET | AL    | Alabaster, Shelby County Airport            | 33.1783  | -86.7817  |
| KGAD | AL    | Gadsden, Gadsden Municipal Airport          | 33.9667  | -86.0833  |
|...   | ...   | ...                                         | ...      | ...       |

Also in the master database, there is a table for each of the stations in the stations table containing the individual observations:

(Sample data from K79J table)

| Date | Time | Wind | Visibility | Weather | Sky Condition | Air Temp | Dew Point | 6HR Max | 6HR Min | Humidity | Wind Chill | Heat Index | Altimeter | Sea Level | 1HR Precip. | 3HR Precip. | 6HR Precip. |
|------------|-------|--------|-------|---------------------|----------------------|-----|------|-----|-----|-----|----|----|-------|--------|------|------|------|
| 12/30/2018 | 10:56 | SW 6   | 10.00 | Overcast            | OVC006               | 74  | 69   |     |     | 85% | NA | NA | 30.12 | 1019.7 |      |      |      |
| 12/30/2018 | 11:56 | Calm   | 6.00  | Light Rain          | BKN006 OVC011        | 74  | 69   | 75  | 67  | 85% | NA | NA | 30.09 | 1018.6 |      |      |      |
| 12/30/2018 | 12:56 | Vrbl 3 | 1.50  | Rain Fog/Mist       | SCT006 BKN023 OVC055 | 73  | 69   |     |     | 87% | NA | NA | 30.07 | 1018.0 | 0.07 |      |      |
| 12/30/2018 | 13:56 | Calm   | 5.00  | Light Rain Fog/Mist | BKN007 OVC016        | 73  | 69   |     |     | 87% | NA | NA | 30.07 | 1017.8 | 0.01 |      |      |
| 12/30/2018 | 14:56 | Calm   | 4.00  | Light Rain Fog/Mist | BKN006 OVC031        | 72  | 68   |     |     | 87% | NA | NA | 30.08 | 1018.2 | 0.16 | 0.24 |      |
| 12/30/2018 | 15:56 | Calm   | 5.00  | Light Rain Fog/Mist | OVC012               | 72  | 68   |     |     | 87% | NA | NA | 30.09 | 1018.5 |      |      |      |
| 12/30/2018 | 16:56 | E 6    | 3.00  | Fog/Mist            | BKN003 BKN008 OVC090 | 72  | 68   |     |     | 87% | NA | NA | 30.08 | 1018.1 | 0.03 |      |      |
| 12/30/2018 | 17:56 | E 5    | 5.00  | Fog/Mist            | BKN003 OVC070        | 71  | 68   | 74  | 71  | 90% | NA | NA | 30.08 | 1018.3 |      |      | 0.27 |
| 12/30/2018 | 18:56 | Vrbl 3 | 4.00  | Fog/Mist            | OVC100               | 71  | 67   |     |     | 87% | NA | NA | 30.09 | 1018.6 |      |      |      |
| 12/30/2018 | 19:56 | Vrbl 3 | 6.00  | Fog/Mist            | SCT006 BKN080 OVC095 | 71  | 67   |     |     | 87% | NA | NA | 30.09 | 1018.5 |      |      |      |
| 12/30/2018 | 20:56 | Vrbl 7 | 7.00  | Overcast            | OVC004               | 71  | 67   |     |     | 87% | NA | NA | 30.09 | 1018.6 |      |      |      |
| ...        | ...   | ...    | ...   | ...                 | ...                  | ... | ...  | ... | ... | ... | ...| ...| ...   | ...    | ...  | ...  | ...  |


### DATA MAINTANENCE

In order to maintain the most up-to-date database locally, every 1-2 days (no more than 3 days since the data is pulled from 3 day observational histories), execute

```python3 website/observations.py```

This script takes on average around 25-35 minutes to complete fully, and the website cannot be accessed while an update is occurring.
Hopefully in the future, concurrency will assist in speeding the process of updating the database.

## TESTING

Execute ```pytest``` in the command line to run the test suite.


## TODO

* Update test suite
* Search bar for zip code using search.py
* Styling throughout website
* Clean up machine learning models code
* Interactive station map on main page
* Search page upgrade
* Remove 'dirty' data from observations.db and stations.csv
* Allow get_obserations script to automatically remove 'bad' stations from csv and db
