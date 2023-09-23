from flask import Flask, render_template, request
from bs4 import BeautifulSoup
from flask_sqlalchemy import SQLAlchemy
import requests, json, os, re
app = Flask(__name__)

# Use the context_processor decorator to make the request object available in all templates
@app.context_processor
def inject_request():
  return dict(request=request)

app.config['SECRET_KEY'] = 'IJD'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)

    
# Mysql db
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Biboy_321@localhost/pigcare'
db = SQLAlchemy(app)
app.app_context().push()


# class Users(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(150), nullable=False)
#     email = db.Column(db.String(100), nullable=False, unique=True)

    
class prices(db.Model):
    id = db.Column(db.Integer,primary_key=True )
    price =  db.Column (db.Float ,nullable= False);
    date_of_price = db.Column(db.String(250), nullable=False)
    header = db.Column(db.String(150), nullable=False)
    
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


SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
pork_with_bones_url = os.path.join(SITE_ROOT, "static", "data", "pork_with_bones_price.json")
pork_kasim_url = os.path.join(SITE_ROOT, "static", "data", "pork_kasim_price.json")
live_price_url = os.path.join(SITE_ROOT, "static", "data", "live_weight_price.json")

@app.route("/price")
def price():
    
    try:
        pork_with_bones = json.load(open(pork_with_bones_url))
        pork_kasim = json.load(open(pork_kasim_url))
        live_price = json.load(open(live_price_url))
    except json.decoder.JSONDecodeError:
        
        return render_template("/features/price.html", pork_with_bones = pork_with_bones, live_price=live_price, pork_kasim=pork_kasim, error='error')
    
    
    return render_template("/features/price.html", pork_with_bones = pork_with_bones, live_price=live_price,  pork_kasim=pork_kasim)

# Refresh The Json file by scraping again the website and saving it again in json
@app.route('/price/refresh', methods=['POST','GET'])
def price_scrape():
    
    
    urls = ['https://www.ceicdata.com/en/philippines/retail-price-selected-agricultural-commodities/retail-price-pork-with-bones-region-4a-batangas-city',
            'https://psa.gov.ph/livestock-poultry-iprs/swine/prices?fbclid=IwAR00Bu7aWKomFUmsuoMwD5SIMTKzxLGsn4YQNQsGlTFOmzv5sp8r0HzwacU',
            'https://www.ceicdata.com/en/philippines/retail-price-selected-agricultural-commodities/retail-price-pork-kasim-region-3-central-luzon']

    for url in urls:
        try: 
            response = requests.get(url)
            doc = BeautifulSoup(response.content, "html.parser")
        except requests.exceptions.ConnectionError:
            pork_with_bones = json.load(open(pork_with_bones_url))
            live_price = json.load(open(live_price_url))
            return render_template("/features/price.html", pork_with_bones = pork_with_bones, live_price=pork_with_bones, error='The website that provides informtion have problem....')
        
        
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
            
            data = {'price': price, 'date': date_price, 'header':header, 'a': title, 'href': url}
            
            with open(pork_with_bones_url, 'w') as f:
                json.dump(data, f)
                print("Pork with Bones price scraped and File saved successfully")
        
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

            data = {'price': price, 'date': date_price, 'header':header, 'a': title, 'href': url}

            with open(live_price_url, 'w') as f:
                json.dump(data, f)
                print("Live weight price scraped and File saved successfully")
        
        if url == urls[2]:
        
            table = doc.table
            tr = table.findAll('tr')
            span =tr[1].findAll('span')
            num = tr[1].span.text.strip()
            
            title = doc.title.text
            price = '₱ '+num
            date_price = span[2].text.strip()
            header = doc.css.select_one("div.tt-u").text
            
            data = {'price': price, 'date': date_price, 'header':header, 'a': title, 'href': url}
            
            with open('D:\Thesis-Source-Code\PigCare\static\data\pork_kasim_price.json', 'w') as f:
                json.dump(data, f)
                print("Pork kasim price scraped and File saved successfully")
                
        pork_with_bones = json.load(open(pork_with_bones_url))
        pork_kasim = json.load(open(pork_kasim_url))
        live_price = json.load(open(live_price_url))
        
    return render_template("/features/price.html", pork_with_bones = pork_with_bones, live_price=live_price, pork_kasim=pork_kasim) # render the results template with the scraped data