# Collecting data from NOAA based on a given station's code (e.g. KTOL for Toledo, Ohio)

Basic web backend exercise covering the following topics:

* databases (sqlite3)
* web scraping (beautifulsoup)
* basic webdev (flask, jinja2)
* restful api & http requests w/ flask

To run the project, execute ```python run.py```

## ABOUT THE PROJECT

NOAA provides 3-day histories of observations for over 2000 weather stations, and updates them every 20 minutes or hour depending on the station. However, there is no easily findable resource containing similar hourly histories online. The goal of this project is to collect the given observation data and compile them into a database containing historical hourly data around the country for much longer than 3 days. It also serves as a basic data collection exercise, along with a unique opportunity to explore weather trends in the country over time as the database becomes more complete.

## COMMAND LINE TOOLS

There are mutliple tools to visualize data in the command line:

1. ```python src/show_stations.py``` shows all of the available station data.
2. ```python src/show_observations.py [station]``` shows all of the available observation data for the station. If no station is specified, the default station specified in the script is used.
3. (WORK IN PROGRESS) ```python src/view_observations.py [station]``` will show a plot of the temperature (and more) for the specified station over all observations.

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

When exporting to a csv file using the db_to_csv.py script, each individual observation is prepended with the station so that the data can be put into the correct table in the observations database.

### DATA MAINTANENCE

I will get around to hosting a base csv file (or db file if I can) containing all of the data I have collected since the genesis of the project (since about Christmas 2018 for most stations). A csv file will likely be the best way to start since it is about half of the size of the db file, and I am wokring on a csv_to_db script that will create the observations.db file from the imported csv file.

In order to maintain the most up-to-date database locally, every 2 days (no more than 3 days since the data is pulled from 3 day observational histories), execute

```python src/get_observations.py```

~~Depending on the internet connection, the script may need to be run more than one time (there are 2190 stations meaning 2190 web requests need to be made so it may timeout with poor connections).
In my experience, each table takes about 0.7-0.8 seconds to complete, however, roadblocks occur relatively often where a minute or two goes by before the next station is updated. In total, it
usually takes no more than 45 minutes to an hour to complete assuming the connection does not time out. Eventually, the script will be refactored to either become more proficient in scraping
or at least able to restart itself in case of timeout.~~

UPDATE: The new script iteratively re-requests the html files that timeout after a specified number of seconds (default is 3 seconds) until there are no more requests that need to be made. This allows for a complete update of the database to occur without needing to manually restart the get_observations.py script and praying the same timeout does not occur. It also ensures that disconnections are avoided, since the script will not automatically timeout when it hits a wall in the urllib request connection. Still a work in progress but a good step nonetheless. The timeout parameter may also be adjusted, 5 seconds just seemed like a reasonable medium since most requests take a second or two; the list storing the timed out stations needs to be relatively short so many rounds of reconnection can be avoided.

Hopefully in the future, concurrency will assist in speeding the process of updating the database.

## TODO

* Host data in different formats elsewhere online
* Better SQL script for creating database and station tables
* Fix date plotting issue (over 2018-19 gap)
* HTML templates for header, footer, or other commonly used formats
* Develop specific views (see flask website github for inspiration)

## LONG TERM GOALS

* Optimize data collection (currently takes about ~30-40 minutes to collect -> sometimes doesn't complete)
* Add hourly forecast viewing (which are also available online per station)
* Machine learning?!?!?
