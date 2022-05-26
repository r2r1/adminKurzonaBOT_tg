import sqlite3


conn = sqlite3.connect('KURZONA.db', check_same_thread=False)                        
cursor = conn.cursor()

sqlite_create_table_query = '''CREATE TABLE kurzona ( 
                            coords TEXT NOT NULL,
                            adress TEXT NOT NULL,
                            photo TEXT NOT NULL);'''
cursor.execute(sqlite_create_table_query)
conn.commit()    