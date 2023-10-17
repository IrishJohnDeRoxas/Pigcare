import mysql.connector

mydb = mysql.connector.connect(
    host="localhost", 
    user='root', 
    passwd='Biboy_321' 
)

my_cursor = mydb.cursor()

# my_cursor.execute('CREATE DATABASE pigcare')

my_cursor.execute('SHOW DATABASES')

for db in my_cursor:
    print(db)
