import os
import sys
import datetime
import sqlite3
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import tabulate

STATION = "KTOL"
#ROOT_DIR =

if __name__=="__main__":
	if len(sys.argv) > 1:
		STATION = str(sys.argv[1])
	else:
		pass
	
	try:
		con = sqlite3.connect(f"databases/{STATION}.db")
	except:
		raise Exception(f"Was not able to connect to {STATION} database")
		
	"""	
	cur = con.cursor()
	try:
		query = cur.execute(f"select date, time, "air temperature", "dew point", "wind chill", "altimeter pressure" from observations order by date, time")
	except sqlite3.OperationalError:
		pass

	x = []
 	y_alt = []
	y_temp = []
	y_dew = []
	for row in query:
		datetime_object = datetime.datetime.strptime("{} {}".format(row[0], row[1]), "%m/%d/%Y %H:%M")	
	
		x.append(datetime_object)
		y_alt.append(float(row[5]))
		y_temp.append(int(row[2]))
		y_dew.append(int(row[3]))
	
	plt.plot(x, y_temp, 'k')
	plt.plot(x, y_dew, 'g')

	plt.plot(x, y_alt, 'k')

	plt.show()
	"""

	query = f"""select * from observations order by date, time"""
	df = pd.read_sql_query(query, con)
	plt.plot([datetime.datetime.strptime('{} {}'.format(df["Date"][i], df["Time"][i]), '%m/%d/%Y %H:%M') for i in range(len(df["Date"]))], list(map(int, df["Dew Point"])))
	plt.show()
