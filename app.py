from flask import Flask, render_template, request, redirect, url_for
from bs4 import BeautifulSoup
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, inspect, create_engine, select
import requests, json, os, re, threading

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import smtplib, time

from datetime import datetime, timedelta
from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.validators import DataRequired, Email, Optional,ValidationError, InputRequired
from wtforms.fields import DateField, EmailField, SelectMultipleField, SelectField
from wtforms.widgets import CheckboxInput, ListWidget, RadioInput


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Biboy_321@localhost/pigcare'
db = SQLAlchemy(app)

engine = create_engine('mysql+pymysql://root:Biboy_321@localhost/pigcare')
inspector = inspect(engine)


SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

# Use the context_processor decorator to make the request object available in all templates
@app.context_processor
def inject_request():
  return dict(request=request)

app.config['SECRET_KEY'] = 'IJD'
app.app_context().push()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
    
    
@app.route("/")
def index():
  # Render the template with the page name as an argument
  return render_template("index.html")

#---------------------Symptom Analysis-------------------------------
class disease_name(db.Model):
    __tablename__ = 'disease_name' # Change the table name
    DN_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column (db.VARCHAR(255), unique=True)
    
class symptoms(db.Model):
    __tablename__ = 'symptoms' # Change the table name
    S_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symptom = db.Column (db.VARCHAR(255), unique=True)

class preventions(db.Model):
    __tablename__ = 'preventions' # Change the table name
    P_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    prevention = db.Column (db.VARCHAR(255), unique=True)

class disease_and_symptom(db.Model):
    __tablename__ = 'disease_and_symptom' # Change the table name
    DS_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    disease_name =  db.Column (db.VARCHAR(255), nullable=False, unique=True)
    symptom = db.Column (db.VARCHAR(255))

class disease_and_prevention(db.Model):
    __tablename__ = 'disease_and_prevention' # Change the table name
    DP_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    disease_name =  db.Column (db.VARCHAR(255), nullable=False, unique=True)
    prevention = db.Column (db.VARCHAR(255))

class disease_and_desc(db.Model):
    __tablename__ = 'disease_and_desc' # Change the table name
    DD_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    disease_name =  db.Column (db.VARCHAR(255))
    desc = db.Column (db.TEXT())
    
class disease_and_treatment(db.Model):
    __tablename__ = 'disease_and_treatment' # Change the table name
    Dt_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    disease_name =  db.Column (db.VARCHAR(255))
    treatment = db.Column (db.TEXT())

                   
class symptoms_select(FlaskForm):
    symptoms_field = SelectMultipleField('Symptoms', 
                                         option_widget=CheckboxInput(), 
                                         widget=ListWidget(prefix_label=False),
                                         validators=[])
    submit_field = SubmitField('Next')
    
    def validate_symptoms_field(self, symptoms_field):
        if len(symptoms_field.data) == 0:
            raise ValidationError("You must select at least one symptom")
       
class disease_select(FlaskForm):
    
    disease_field = SelectMultipleField('Disease', 
                                option_widget=RadioInput(), 
                                widget=ListWidget(prefix_label=False),
                                validators=[])
    submit_field = SubmitField('Next')
    go_back = SubmitField('Go Back', render_kw={'formnovalidate': True,
                                                'onclick': 'history.back()',
                                                'type':False})
    def validate_disease_field(self, disease_field):
        if len(disease_field.data) == 0:
            raise ValidationError("Select Atleast one Disease")

@app.route('/symptom_analysis', methods=['GET', 'POST'])
def symptom_analysis():
    # Get user input symptom, proccess it into posible disease
    form = symptoms_select()
    choices_db = symptoms.query.all()
    choices=[choice.symptom for choice in choices_db]
    form.symptoms_field.choices = choices
    
    if form.validate_on_submit():
        user_input_symptom = request.form.getlist('symptoms_field')
        return redirect(url_for('possible_disease', user_input_symptom = user_input_symptom))
        
    return render_template('features/symptom_analysis.html', form=form)

@app.route('/symptom_analysis/possible_disease', methods=['GET', 'POST'])
def possible_disease():
    # Get data from user input and get the posible diseasefrom db
    user_input_symptom = request.args.getlist('user_input_symptom')
    
    possible_disease_db = []
    for i in range(len(user_input_symptom)):
        disease_name_db = disease_and_symptom.query.filter_by(symptom = user_input_symptom[i]).all()
        for dn in disease_name_db:
            possible_disease_db.append(dn.disease_name)
      
    return render_template('features/possible_disease.html', user_input_symptom = user_input_symptom,
                           possible_disease_db = list(set(possible_disease_db)) )
        
@app.route('/symptom_analysis/possible_disease/<disease>/desc')
def disease_desc(disease):
 
    user_input_disease = disease
    print(user_input_disease)
    # TODO get the treatment and prevention for the user_input_disease
    desc = disease_and_desc.query.filter_by(disease_name = user_input_disease).first()
    treatments_query = disease_and_treatment.query.filter_by(disease_name = user_input_disease).all()
    preventions_query = disease_and_prevention.query.filter_by(disease_name = user_input_disease).all()
    print(preventions_query)
    return render_template('features/disease_desc.html', desc= desc.desc,
                           treatments_query=treatments_query, preventions_query=preventions_query )  
 
#---------------------End of Symptom Analysis------------------------


#---------------------Nutrition--------------------------------------

class author_nutrition_info(db.Model):
    __tablename__ = 'author_nutrition_info' # Change the table name
    id = db.Column(db.Integer, primary_key=True)
    title =  db.Column (db.String(500) ,nullable= False)
    author =  db.Column (db.String(500) ,nullable= False)
    author_desc =  db.Column (db.String(500) ,nullable= False)
    
class main_nutrition_info(db.Model):
    __tablename__ = 'main_nutrition_info' # Change the table name
    id = db.Column(db.Integer, primary_key=True)
    header =  db.Column (db.String(300) ,nullable= False)
    desc = db.Column(db.Text(16383), nullable=False)
    
class sub_nutrition_info(db.Model):
    __tablename__ = 'sub_nutrition_info' # Change the table name
    id = db.Column(db.Integer, primary_key=True)
    sub_header =  db.Column (db.String(300) ,nullable= False)
    sub_desc = db.Column(db.String(5000), nullable=False)

@app.route("/nutrition")
def nutrition():
    """Get the data from db into db

    Returns:
        template: /features/nutrition.html"
        contents and author query
    """
    
    author = author_nutrition_info.query.all()
    contents = main_nutrition_info.query.all()
    return render_template("/features/nutrition.html", author = author, contents = contents)

#---------------------End of Nutrition-------------------------------


#---------------------Facts------------------------------------------

class facts_about_pigs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title =  db.Column (db.String(300) ,nullable= False)
    desc = db.Column(db.String(2000), nullable=False)

@app.route("/facts")
def facts():
    """Get the data from db into Front End

    Returns:
        template: /features/facts.html"
        data facts and facts_resume query
    """
    
    facts =  facts_about_pigs.query.all()[3:]
    facts_resume = facts_about_pigs.query.all()[:3]
    
    # facts origin url, index 0
    # facts_resume origin url, index 1
    
    urls = ['https://www.coolkidfacts.com/facts-about-pigs/', 'https://kids.nationalgeographic.com/animals/mammals/facts/pig']
    
    return render_template("/features/facts.html", facts = facts, facts_resume = facts_resume, urls = urls)

#---------------------End of Types-----------------------------------

#---------------------Types------------------------------------------

class types_of_pigs(db.Model):
    id = db.Column(db.Integer,primary_key=True )
    title =  db.Column (db.String(250) ,nullable= False)
    desc = db.Column(db.String(1500), nullable=False)
    a = db.Column(db.String(1500), nullable=False)
    img_url = db.Column(db.String(1500), nullable=False)
    
    # # Checks if table exists in db, if not create using db.model
    # table_exists = inspector.has_table('types_of_pigs')# <- Change Table name
    # if table_exists:
    #     # print('The table exists.') 
    #     pass
    # else:
    #     with app.app_context():
    #         db.create_all()
    #     print('The table does not exist, Creating one now...') 
    
        
@app.route("/types")
def types():
    """Get 6 common types in db, display it in Front-end

    Returns:
        template: /features/types.html
        data: 6 common types query
    """
    
    twenty_types = types_of_pigs.query.all()
    common_types = [twenty_types[0],twenty_types[1], twenty_types[2],
                    twenty_types[5], twenty_types[7],twenty_types[17] ]

    return render_template("/features/types.html", common_types = common_types)

#---------------------End of Types-----------------------------------


#---------------------Calender---------------------------------------

# Future update: use celery to handle the asych To delay the sending of an email in Celery, you can use the apply_async()
# method with the countdown or eta parameter. The countdown parameter specifies the number of seconds 
# to wait before executing the task, while the eta parameter specifies the exact date and time to execute the task

class get_user_info(FlaskForm):
    date_field = DateField('Start Date: ',  validators=[DataRequired()])
    email_field = EmailField('Enter Email: ', validators=[DataRequired(), Email()])
    submit_field = SubmitField('Start')
    
@app.route("/calendar")
def calendar():
    """Display information (hardcoded) about due date of pigs

    Returns:
        template: /features/calendar.html
    """
    
    return render_template("/features/calendar.html")

@app.route("/calendar/send_emails", methods=['GET', 'POST'])
def send_mail():
    """Prepare the emails to be sent 

    Returns:
        template: /features/send_mail.html
        data: form 
    """
    
    form = get_user_info()
    due_date = None
    if form.validate_on_submit():
        
        date = form.date_field.data
        email = form.email_field.data   
        print(date,email)   
        exact_date = date + timedelta(days=114)
        two_weeks_before_due = exact_date - timedelta(days=12)
        two_days_before_due = exact_date - timedelta(days=2)

        exact_date_str = exact_date.strftime('%A, %d %B %Y')
        two_weeks_before_due_str = two_weeks_before_due.strftime('%A, %d %B %Y')
        two_days_before_due_str = two_days_before_due.strftime('%A, %d %B %Y')

        due_date = {
            'exact_date': exact_date_str,
            'two_weeks': two_weeks_before_due_str,
            'two_days': two_days_before_due_str
        }
        
        my_thread = threading.Thread(target=send_emails, args=(email,date))
       # Create a new thread
 
        # Start the new thread
        my_thread.start()
        form.date_field.data = '' 
        form.email_field.data  = ''
    return render_template("/features/send_mail.html", form = form, due_date=due_date)

def send_emails(receiver_email, date):
    """ On click start new thread and send the emails, 2weeks, 2days notif """
    
    
    sender = 'pigcarethesis@gmail.com'
    password = 'vnku mpel fxzo wmxc'
    receiver = receiver_email

    # Create a message object
    msg1 = MIMEMultipart()

    # Set the sender and recipient
    msg1['From'] = sender
    msg1['To'] = receiver

    # Set the subject
    msg1['Subject'] = 'Reminder: Due Date 2 weeks aaaa'

    # # Add an image to the email
    # with open('image.jpg', 'rb') as f:
    #     img_data = f.read()
    # img = MIMEImage(img_data)
    # msg1.attach(img)
    
   
    
    # Convert the date object to a datetime object
    datetime_from_user = datetime.combine(date, datetime.min.time())
    
    # Calculate the 2 weeks and 2 days from now...... For the demonstration its set for 60 secs and 40 secs
    two_weeks_before_due_date = datetime_from_user + timedelta(seconds=60) 
    two_days_before_due_date = datetime_from_user + timedelta(seconds=40)
    
    # two_weeks_before_due_date = datetime_from_user + timedelta(days=102) 
    # two_days_before_due_date = datetime_from_user + timedelta(days=112)
    
    
    # Calculate the number of seconds between now and the future time
    first_reminder = (two_weeks_before_due_date - datetime_from_user).total_seconds()
    second_reminder = (two_days_before_due_date - datetime_from_user).total_seconds()
    
    print(first_reminder, second_reminder)



    # Format the date object into a string and insert it into the HTML content
    html1 = f"""
    <html>
    <head>
        <style>
        p {{
            text-align: center;
            color: blue;
        }}
    </style>
    </head>
    <body>
        <h1>2 week reminder</h1>
        <hr>
        <h3>
            PigcCare thesis reminder - {two_weeks_before_due_date.strftime('%a, %d %b %Y')}
        </h3>
    </body>
    </html>
    """
    reminder_email_1 = MIMEText(html1, 'html')
    msg1.attach(reminder_email_1)

    time.sleep(first_reminder) 

    # Send the email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg1.as_string())
        print("email 1 sent")
    
    #------------------------------------------------------------------------------------ 
    # Set the sender and recipient
    msg2 = MIMEMultipart()

    msg2['From'] = sender
    msg2['To'] = receiver

    # Set the subject
    msg2['Subject'] = 'Reminder: Due Date 2 days bbbb'

    # # Add an image to the email
    # with open('image.jpg', 'rb') as f:
    #     img_data = f.read()
    # img = MIMEImage(img_data)
    # msg2.attach(img)


    # Format the date object into a string and insert it into the HTML content
    html2 = f"""
    <html>
    <head>
        <style>
        p {{
            text-align: center;
            color: blue;
        }}
    </style>
    </head>

    <body>
        <h1>2 days reminder</h1>
        
        <hr>
        <h3>
            PigcCare thesis reminder - {two_days_before_due_date.strftime('%a, %d %b %Y - %H:%M:%S')}
        </h3>
        
        
    </body>
    </html>
    """
    reminder_email_2 = MIMEText(html2, 'html')
    msg2.attach(reminder_email_2)

    time.sleep(second_reminder)
    # Send the email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg2.as_string())
        print("email 2 sent")

#---------------------End of Calender-----------------------------------
        
        
#---------------------News----------------------------------------------       
 
class scraped_news(db.Model):
    id = db.Column(db.Integer,primary_key=True )
    type = db.Column(db.String(250), nullable=False)
    title =  db.Column (db.String(250) ,nullable= False)
    date = db.Column(db.String(250), nullable=False)
    desc = db.Column(db.String(400), nullable=False)
    a = db.Column(db.String(1500), nullable=False)
    img_url = db.Column(db.String(1500), nullable=False)
    
    # Checks if table exists in db, if not create using db.model
    # table_exists = inspector.has_table('scraped_news')
    # if table_exists:
    #     # print('The table exists.') 
    #     pass
    # else:
    #     with app.app_context():
    #         db.create_all()
    #     print('The table does not exist, Creating one now...')  
       
@app.route("/news")
def news():
    """Get news from db and show it in Front end

    Returns:
        template: /features/news.html
        data: dbarticles and dbnews(query)
    """
    
    dbarticles = scraped_news.query.filter_by(type = 'article').all()
    dbnews = scraped_news.query.filter_by(type = 'news').all()
    

    db.session.commit()

    return render_template("/features/news.html", dbnews = dbnews, dbarticles = dbarticles, )

@app.route("/news/scrape-news")
def scrape_news():
    """On windows load in news, update the news card UI

    Returns:
        template: /features/scrape_news.html
        data: dbarticles and dbnews(scraped and query it)
    """
    
    today = datetime.today()

    dbdate = db.session.query(scraped_news.date).first()
    datetime_object = datetime.strptime(dbdate[0], "%B %d, %Y")
    # Check if url of the website being scrape is working.
    try: 
        urls = ['https://www.swineweb.com/', 'https://www.thepigsite.com/'] 
    
        for url in urls:
            response = requests.get(url)
            doc = BeautifulSoup(response.content, "html.parser")
            # Updates the scraped articles
            if url == urls[0]:
                articles = doc.css.select('div.td_module_14 ')
                dbarticles = scraped_news.query.filter_by(type = 'article').all()
                
                # Loop the scrape article 3 times and update db
                for counter in range(3):
                    article = articles[counter]
                    desc_format = article.css.select_one(
                        'div.td-excerpt').text.strip().replace('\r\n\r\n\r\n\r\n', '')
                    remove_read_more = desc_format.replace('Read more', '').strip()
                    desc_split = remove_read_more.split()
                    link = article.css.select_one('div.td-read-more a')
                    img = article.css.select_one('img.entry-thumb')

                    title = article.css.select_one('h3.entry-title').text
                    date = article.find('time').text
                    desc = ' '.join(desc_split[:9]) + '...'
                    a = link.get('href')
                    img_url = img.get('data-img-url')

                    dbarticle = dbarticles[counter]
                    dbarticle.title = title
                    dbarticle.date = date
                    dbarticle.desc = desc
                    dbarticle.a = a
                    dbarticle.img_url = img_url
                    db.session.commit()
                    
            # Updates scraped news
            if url == urls[1]:
                latest_news_container = doc.css.select('section.content-block')[2]
                news_divs = latest_news_container.css.select('div.col-md-12')
                dbnews_all = scraped_news.query.filter_by(type = 'news').all()
                
                # Loop the scrape news 3 times and update db
                for counter in range(3):
                    news = news_divs[counter]
                    link = news.css.select_one('div.article-summary-title a')
                    date_text = news.css.select_one('span.align-items-center').text.strip()
                    format_date = date_text.split()

                    title = news.css.select_one('div.article-summary-title').text.strip()
                    date = format_date[1] + ' ' + format_date[0] + ", " + format_date[2]
                    desc = news.css.select_one('div.article-summary-text').text.strip() + '...'
                    img_url = news.css.select_one('a.article-summary-image img').get('src')
                    a = link.get('href')
                    
                    dbnews = dbnews_all[counter]
                    dbnews.title = title
                    dbnews.date = date
                    dbnews.desc = desc
                    dbnews.a = a
                    dbnews.img_url = img_url
                    db.session.commit()
                    
        dbarticles = scraped_news.query.filter_by(type = 'article').all()
        dbnews = scraped_news.query.filter_by(type = 'news').all()
        db.session.commit()

        return render_template("/features/scrape_news.html", dbnews = dbnews, dbarticles = dbarticles,)
        
    except requests.exceptions.ConnectionError:
        
        dbarticles = scraped_news.query.filter_by(type = 'article').all()
        dbnews = scraped_news.query.filter_by(type = 'news').all()
        
        db.session.commit()

        return render_template("/features/news.html", dbnews = dbnews, dbarticles = dbarticles)
        
#---------------------End of News---------------------------------------


#---------------------Prices--------------------------------------------

class prices(db.Model):
    id = db.Column(db.Integer,primary_key=True )
    type = db.Column(db.String(250), nullable=False)
    price =  db.Column (db.String(250) ,nullable= False)
    date_of_price = db.Column(db.String(250), nullable=False)
    header = db.Column(db.String(150), nullable=False)
    a = db.Column(db.String(150), nullable=False)
    href = db.Column(db.String(1000), nullable=False)
# TODO 2 query the prices better

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
    """Get the prices from db and pass it in UI
    
    Return:
        template: /features/price.html
        data: prices from db
    """
    db.session.commit()

    return render_template("/features/price.html", pork_with_bones = pork_with_bones, 
                           live_weight=live_weight,  pork_kasim=pork_kasim)

# Refresh button to scrape again the sites, and save in db. insert sql
@app.route('/price/refresh', methods=['POST','GET'])
def price_scrape():
    """On refresh click this will run, scraping prices and updating UI
    
    Returns:
        template: /features/price.html
        data: prices from internet
    """
    
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
    
#---------------------End of Prices-----------------------------------------