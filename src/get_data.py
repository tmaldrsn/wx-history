import sqlite3

def main(station):
	print(f"DATA FROM STATION {station}")

	con = sqlite3.connect(f"databases/{station}.db")
	cur = con.cursor()

	for row in cur.execute("select * from observations order by date, time"):
		print(row)
	

if __name__=='__main__':
	STATION = "KTOL"
	main(STATION)
