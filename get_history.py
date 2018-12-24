import sys
import datetime
import urllib.request
import sqlite3
from bs4 import BeautifulSoup

STATION = "KTOL"


if __name__ == "__main__":
	url = urllib.request.urlopen("https://w1.weather.gov/data/obhistory/" + STATION + ".html")
	soup = BeautifulSoup(url, 'html.parser')

	forecast_table = soup.find_all('table')[3]	
	forecast_rows = forecast_table.find_all('tr')[3:-3]

	forecast_elements = [
		"Date", 
		"Time", 
		"Wind", 
		"Visibility", 
		"Weather", 
		"Sky Condition", 
		"Air Temperature", 
		"Dew Point", 
		"6HR Max", 
		"6HR Min", 
		"Humidty", 
		"Wind Chill", 
		"Heat Index", 
		"Altimeter Pressure", 
		"Sea Level Pressure", 
		"1HR Precip", 
		"3HR Precip", 
		"6HR Precip"
	]

	# Create a database (in memory for now)
	con = sqlite3.connect(":memory:")

	# Create the forecast table
	con.execute(f"""create table observations({','.join('"{0}"'.format(w) for w in forecast_elements)})""")
	data_rows = [[element.string for element in row.find_all('td')] for row in forecast_rows]
	
	# Insert data into forecast table
	con.executemany(f"""insert into observations values ({','.join(['?' for i in range(len(forecast_elements))])})""", data_rows)
	
	# Print the table contents
	for row in con.execute("select date, time from observations"):
		print(row) 
