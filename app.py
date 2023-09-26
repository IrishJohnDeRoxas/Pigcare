from flask import Flask, render_template, request
from bs4 import BeautifulSoup
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, inspect, create_engine
import requests, json, os, re


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Biboy_321@localhost/pigcare'
db = SQLAlchemy(app)


SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

# Use the context_processor decorator to make the request object available in all templates
@app.context_processor
def inject_request():
  return dict(request=request)

app.config['SECRET_KEY'] = 'IJD'
app.app_context().push()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)

    
class prices(db.Model):
    id = db.Column(db.Integer,primary_key=True )
    type = db.Column(db.String(250), nullable=False)
    price =  db.Column (db.String(250) ,nullable= False)
    date_of_price = db.Column(db.String(250), nullable=False)
    header = db.Column(db.String(150), nullable=False)
    a = db.Column(db.String(150), nullable=False)
    href = db.Column(db.String(1000), nullable=False)
    
    
    
@app.route("/")
def index():
  # Render the template with the page name as an argument
  return render_template("index.html")

@app.route("/symptom_analysis")
def symptom_analysis():
  # No need to pass the request object explicitly
  return render_template("features/symptom_analysis.html")

@app.route("/nutrition")
def nutrition():
    return render_template("/features/nutrition.html")

@app.route("/facts")
def facts():
    return render_template("/features/facts.html")

@app.route("/types")
def types():
    return render_template("/features/types.html")

@app.route("/calendar")
def calendar():
    return render_template("/features/calendar.html")

@app.route("/news")
def news():
    return render_template("/features/news.html")


# pork_with_bones_url = os.path.join(SITE_ROOT, "static", "data", "pork_with_bones_price.json")
# pork_kasim_url = os.path.join(SITE_ROOT, "static", "data", "pork_kasim_price.json")
# live_price_url = os.path.join(SITE_ROOT, "static", "data", "live_weight_price.json")



# Getting the information from db and storing in dictionary
result = db.session.execute(text('SELECT * FROM prices'))

prices_fetch = result.fetchall()


live_weight_fetch = prices_fetch[0]
pork_with_bones_fetch = prices_fetch[1]
pork_kasim_fecth = prices_fetch[2]

pork_with_bones = {
    'id': pork_with_bones_fetch[0],
    'type': pork_with_bones_fetch[1],
    'price': pork_with_bones_fetch[2],
    'date': pork_with_bones_fetch[3],
    'header': pork_with_bones_fetch[4],
    'a': pork_with_bones_fetch[5],
    'href': pork_with_bones_fetch[6]
}
live_weight = {
    'id': live_weight_fetch[0],
    'type': live_weight_fetch[1],
    'price': live_weight_fetch[2],
    'date': live_weight_fetch[3],
    'header': live_weight_fetch[4],
    'a': live_weight_fetch[5],
    'href': live_weight_fetch[6]
}
pork_kasim = {
    'id': pork_kasim_fecth[0],
    'type': pork_kasim_fecth[1],
    'price': pork_kasim_fecth[2],
    'date': pork_kasim_fecth[3],
    'header': pork_kasim_fecth[4],
    'a': pork_kasim_fecth[5],
    'href': pork_kasim_fecth[6]
}


@app.route("/price")
def price():
    
    # engine = create_engine('mysql+pymysql://root:Biboy_321@localhost/pigcare')
    # inspector = inspect(engine)
    # table_exists = inspector.has_table('prices')

    # if table_exists:
    #     print('The table exists.')
    # else:
    #     print('The table does not exist.')
    
    if isinstance(prices(), db.Model):
        print('The class has been created.')
    else:
        print('The class has not been created.')
    
    try:
        db.session.execute(text('SELECT 1'))
        print('Connection successful!')
    except Exception as e:
        print('Connection failed! Error:', e)
    
    db.session.commit()

    return render_template("/features/price.html", pork_with_bones = pork_with_bones, 
                           live_weight=live_weight,  pork_kasim=pork_kasim)

# TODO Refresh button to scrape again the sites, and save in db. insert sql
@app.route('/price/refresh', methods=['POST','GET'])
def price_scrape():
    
    
    urls = ['https://www.ceicdata.com/en/philippines/retail-price-selected-agricultural-commodities/retail-price-pork-with-bones-region-4a-batangas-city',
            'https://psa.gov.ph/livestock-poultry-iprs/swine/prices?fbclid=IwAR00Bu7aWKomFUmsuoMwD5SIMTKzxLGsn4YQNQsGlTFOmzv5sp8r0HzwacU',
            'https://www.ceicdata.com/en/philippines/retail-price-selected-agricultural-commodities/retail-price-pork-kasim-region-3-central-luzon']

    for url in urls:
        # Checkk if url of the website being scrape is working.
        try: 
            response = requests.get(url)
            doc = BeautifulSoup(response.content, "html.parser")
        except requests.exceptions.ConnectionError:
            error_message = 'The website that provides informtion have problem....'
            return render_template("/features/price.html", pork_with_bones = pork_with_bones, 
                                   live_weight=live_weight, pork_kasim=pork_kasim ,error=error_message)
        
        
        # Pork with Bones price scrape
        if url == urls[0]: 
            table = doc.table
            tr = table.findAll('tr')
            span =tr[1].findAll('span')
            num = tr[1].span.text.strip()
            
            # title = doc.title.text            
            # date_price = span[2].text.strip()
            # header = doc.css.select_one("div.tt-u").text
            price = '₱ '+num
            
            pork_with_bones['price'] = price
            
            query = prices.query.filter_by(type = 'pork_with_bones').first()
            query.price = price


        # Live weight price scrape
        if url == urls[1]:
            def extract_numbers(text):
                numbers = re.findall(r'\d+', text)
                price =  '.'.join(numbers)
                
                return '₱ '+price

            div = doc.find('div')
            span = div.css.select('span.nowrap')
            # time = div.findAll('time')

            # header = div.css.select_one('h3.page-title').text
            # date_price = time[0].text + ' - ' + time[1].text
            # title = div.css.select_one('h3.field-content').text
            price = extract_numbers(span[0].text)

            live_weight['price'] = price
            
            query = prices.query.filter_by(type = 'live_weight').first()
            query.price = price
        
        if url == urls[2]:
        
            table = doc.table
            tr = table.findAll('tr')
            span =tr[1].findAll('span')
            num = tr[1].span.text.strip()
            
            # title = doc.title.text
            # date_price = span[2].text.strip()
            # header = doc.css.select_one("div.tt-u").text
            price = '₱ '+ num
            
            pork_kasim['price'] = price
            query = prices.query.filter_by(type = 'pork_kasim').first()
            query.price = price
            
    db.session.commit()   
     
    return render_template("/features/price.html", pork_with_bones = pork_with_bones, 
                           live_weight=live_weight, pork_kasim=pork_kasim) # render the results template with the scraped data