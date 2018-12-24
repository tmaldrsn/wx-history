import os
import sqlite3
import get_history
import time

if __name__=="__main__":
	
	start_time = time.time()

	if not os.path.isfile("databases/stations.db"):
		raise Exception("Stations database does not exist!")
	
	con = sqlite3.connect("databases/stations.db")
	cur = con.cursor()

	for row in cur.execute("select id from station"):
		station_id = row[0]
		get_history.main(station_id)
		print(f"Database for {station_id} created!\r", end="")

	end_time = time.time()

	print(f"Total Time Elapsed: {end_time - start_time} seconds")
