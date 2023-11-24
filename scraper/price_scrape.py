from bs4 import BeautifulSoup
import requests, json, os, re, mysql.connector

mydb = mysql.connector.connect(
    host="localhost", 
    user='root', 
    passwd='Biboy_321',
    database='pigcare' 
)

my_cursor = mydb.cursor()
urls = ['https://www.ceicdata.com/en/philippines/retail-price-selected-agricultural-commodities/retail-price-pork-with-bones-region-4a-batangas-city',
        'https://psa.gov.ph/livestock-poultry-iprs/swine/prices?fbclid=IwAR00Bu7aWKomFUmsuoMwD5SIMTKzxLGsn4YQNQsGlTFOmzv5sp8r0HzwacU',
        'https://www.ceicdata.com/en/philippines/retail-price-selected-agricultural-commodities/retail-price-pork-kasim-region-3-central-luzon']

for url in urls:
    
    response = requests.get(url)
    doc = BeautifulSoup(response.content, "html.parser")

    # Pork with Bones price scrape
    if url == urls[0]: 
        table = doc.table
        tr = table.findAll('tr')
        span =tr[1].findAll('span')
        num = tr[1].span.text.strip()
        
        title = doc.title.text
        price = '₱ '+num
        date_price = span[2].text.strip()
        header = doc.css.select_one("div.tt-u").text
        
        query = """
                INSERT INTO prices (`type`, price, date_of_price, header, a, href) 
                VALUES (%s, %s, %s, %s, %s, %s)
                """
        values = ('pork_with_bones', price, date_price, header, title, url) 
        my_cursor.execute(query, values)

        if my_cursor.rowcount > 0:
            print("Query executed successfully")

        
    
    # Live weight price scrape
    if url == urls[1]:
        def extract_numbers(text):
            numbers = re.findall(r'\d+', text)
            price =  '.'.join(numbers)
            
            return '₱ '+price

        div = doc.find('div')
        span = div.css.select('span.nowrap')
        time = div.findAll('time')

        header = div.css.select_one('h3.page-title').text

        price = extract_numbers(span[0].text)
        date_price = time[0].text + ' - ' + time[1].text
        title = div.css.select_one('h3.field-content').text

        query = """
                INSERT INTO prices (`type`, price, date_of_price, header, a, href) 
                VALUES (%s, %s, %s, %s, %s, %s)
                """
        values = ('live_weight', price, date_price, header, title, url) 
        my_cursor.execute(query, values)

        if my_cursor.rowcount > 0:
            print("Query executed successfully")
  
        
    # Pork kasim price scrape 
    if url == urls[2]:
        
        table = doc.table
        tr = table.findAll('tr')
        span =tr[1].findAll('span')
        num = tr[1].span.text.strip()
        
        title = doc.title.text
        price = '₱ '+num
        date_price = span[2].text.strip()
        header = doc.css.select_one("div.tt-u").text
        
        query = """
                INSERT INTO prices (`type`, price, date_of_price, header, a, href) 
                VALUES (%s, %s, %s, %s, %s, %s)
                """
        values = ('pork_kasim', price, date_price, header, title, url) 
        my_cursor.execute(query, values)

        if my_cursor.rowcount > 0:
            print("Query executed successfully")

        
mydb.commit()
my_cursor.close()
mydb.close()