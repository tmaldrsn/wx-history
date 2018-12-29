import os
import sys
import sqlite3
import tabulate

def main(station):

	if not os.path.isfile(f"databases/{station}.db"):
		raise Exception(f"{station} database does not exist!")
	
	con = sqlite3.connect(f"databases/{station}.db")
	cur = con.cursor()

	header_query = "pragma table_info(observations)"
	data_query = "select * from observations order by date, time"

	print(f"DATA FROM STATION {station}")
	print(tabulate.tabulate(list(cur.execute(data_query)), headers=[i[1] for i in list(cur.execute(header_query))], tablefmt="plain"))


if __name__=='__main__':
	if len(sys.argv) == 2:
		STATION = sys.argv[1]
	else:
		STATION = "KTOL"
	main(STATION)
	