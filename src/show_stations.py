import os
import sqlite3
import pandas as pd
import tabulate
import logging

logging.basicConfig(filename="logs/app.log", format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
DB = "observations.db"

if __name__=="__main__":
	try:
		con = sqlite3.connect(DB)
	except:
		raise Exception("Was not able to connect to observations database")

	cur = con.cursor()
	header_query = "pragma table_info(station)"
	data_query = "select * from station"
	
	print("STATION DATA")
	print(tabulate.tabulate(list(cur.execute(data_query)), headers=[i[1] for i in list(cur.execute(header_query))], tablefmt="plain"))	
