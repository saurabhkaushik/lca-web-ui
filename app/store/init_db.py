import sqlite3

connection = sqlite3.connect('database.db')


with open('app/schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO contracts (title, content) VALUES (?, ?)",
            ('First Post', 'Content for the first post')
            )
cur.execute("INSERT INTO learndb (keywords, statements) VALUES (?, ?)",
            ('save, liability, contract, compliance, legal', '')
            )

connection.commit()

connection.close()
