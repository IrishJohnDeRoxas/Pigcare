import mysql.connector

mydb = mysql.connector.connect(
    host="localhost", 
    user='root', 
    passwd='Biboy_321',
    database='pigcare' 
)

my_cursor = mydb.cursor()

my_cursor.execute('SELECT * FROM prices')

prices = my_cursor.fetchall()

pork_with_bones = prices[0]
live_weight = prices[1]
pork_kasim = prices[2]

pork_with_bones = {
    'id': pork_with_bones[0],
    'type': pork_with_bones[1],
    'price': pork_with_bones[2],
    'date': pork_with_bones[3],
    'header': pork_with_bones[4],
    'a': pork_with_bones[5],
    'href': pork_with_bones[6]
}
live_weight = {
    'id': live_weight[0],
    'type': live_weight[1],
    'price': live_weight[2],
    'date': live_weight[3],
    'header': live_weight[4],
    'a': live_weight[5],
    'href': live_weight[6]
}
pork_kasim = {
    'id': pork_kasim[0],
    'type': pork_kasim[1],
    'price': pork_kasim[2],
    'date': pork_kasim[3],
    'header': pork_kasim[4],
    'a': pork_kasim[5],
    'href': pork_kasim[6]
}

print( pork_with_bones['price'], live_weight['price'], pork_kasim['price'],)