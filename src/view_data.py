import os
import sys
import datetime
import sqlite3
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import tabulate

ITEMS = "Air Temperature"

if __name__=="__main__":
	if len(sys.argv) > 1:
		STATION = str(sys.argv[1])
	else:
		print("No station was given as an argument, using KTOL by default.")
		STATION = "KTOL"
	
	try:
		con = sqlite3.connect(f"databases/{STATION}.db")
	except:
		raise Exception(f"Was not able to connect to {STATION} database")
		

	query = f"""select * from observations order by date, time"""
	df = pd.read_sql_query(query, con)
	
	plt.figure()
	plt.title(f"{ITEM} for {STATION}")
	plt.xlabel("Date")
	plt.ylabel(f"{ITEM}")


	plt.plot([datetime.datetime.strptime('{} {}'.format(df["Date"][i], df["Time"][i]), '%m/%d/%Y %H:%M') for i in range(len(df["Date"]))], list(map(int, df[ITEM])))
	plt.show()
