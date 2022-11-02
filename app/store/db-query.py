import sqlite3

connection = sqlite3.connect('database.db')

cur = connection.cursor()
for row in cur.execute('SELECT * FROM querytab'): 
    print(row)

## connection.commit()  
connection.close()
