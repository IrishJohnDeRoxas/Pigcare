import smtplib
import time
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import os
import re
import requests
import threading
import models as table
from config import app, db
from bs4 import BeautifulSoup
from flask import render_template, request, redirect, url_for, flash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import SubmitField
from wtforms.fields import DateField, EmailField, SelectMultipleField, StringField, PasswordField
from wtforms.validators import DataRequired, Email, ValidationError
from wtforms.widgets import CheckboxInput, ListWidget, RadioInput

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))


# Use the context_processor decorator to make the request object available in all templates
@app.context_processor
def inject_request():
    return dict(request=request)


app.config['SECRET_KEY'] = 'IJD'
app.app_context().push()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return AdminModel.query.get(int(user_id))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)


@app.route("/")
def index():
    # Render the template with the page name as an argument
    return render_template("features/base/index.html")


# TODO Update the ERD and DFD


# TODO Add pictures or videos every possible feature
# TODO Add admin page to do CRUD operation for every feature
# TODO Add see more for the possible disease name
# TODO Add Symptom or Disease name to select

# --------------------- Admin ----------------------------------------
class AdminModel(db.Model, UserMixin):
    __tablename__ = 'admin'  # Change the table name
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text(), nullable=False, unique=True)
    pw = db.Column(db.String(), nullable=False)

    @property
    def password(self):
        raise AttributeError('Password is not readable')

    @password.setter
    def password(self, password):
        self.pw = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.pw, password)


class AdminLoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired()])
    password = PasswordField('Password',
                             validators=[DataRequired()])
    submit = SubmitField('Sign In')


@app.route("/admin/login", methods=['GET', 'POST'])
def login():
    selected = 'login'
    form = AdminLoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        admin_creds = AdminModel.query.filter_by(username=username).first()

        if admin_creds:
            if check_password_hash(admin_creds.pw, password):
                login_user(admin_creds)
                flash(f'Hello, {admin_creds.username}')
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password")
        else:
            flash("No account found with that Username")

    return render_template("admin/base/login.html", form=form, selected=selected)


@app.route("/admin/logout")
@login_required
def logout():
    logout_user()
    flash('Logged out')
    return redirect(url_for('index'))


@app.route("/admin/dashboard")
@login_required
def dashboard():
    selected = 'dashboard'
    return render_template("admin/base/dashboard.html", selected=selected)


# --------------------- End of Admin ---------------------------------

# ---------------------Symptom Analysis-------------------------------


class SymptomForm(FlaskForm):
    symptoms_field = SelectMultipleField('Symptoms',
                                         option_widget=CheckboxInput(),
                                         widget=ListWidget(prefix_label=False),
                                         validators=[])
    submit_field = SubmitField('Next')

    @staticmethod
    def validate_symptoms_field(self, symptoms_field):
        if len(symptoms_field.data) == 0:
            raise ValidationError("You must select at least one symptom")


class DiseaseForm(FlaskForm):
    disease_field = SelectMultipleField('Disease',
                                        option_widget=RadioInput(),
                                        widget=ListWidget(prefix_label=False),
                                        validators=[])
    submit_field = SubmitField('Next')
    go_back = SubmitField('Go Back', render_kw={'form-novalidate': True,
                                                'onclick': 'history.back()',
                                                'type': False})

    @staticmethod
    def validate_disease_field(self, disease_field):
        if len(disease_field.data) == 0:
            raise ValidationError("Select at least one disease")


@app.route('/admin/symptom', methods=['GET', 'POST'])
@login_required
def admin_symptom():
    selected = 'admin_symptom'
    return render_template('admin/control/admin_symptom.html', selected=selected)


@app.route('/symptom_analysis', methods=['GET', 'POST'])
def symptom_analysis():
    # Get user input symptom, process it into possible disease
    selected = 'symptom'
    form = SymptomForm()
    choices_db = table.Symptoms.query.all()
    choices = [choice.symptom for choice in choices_db]
    form.symptoms_field.choices = choices

    if form.validate_on_submit():
        user_input_symptom = request.form.getlist('symptoms_field')
        return redirect(url_for('possible_disease',
                                user_input_symptom=user_input_symptom,
                                selected=selected))

    return render_template('features/symptom_analysis.html', selected=selected,
                           form=form)


@app.route('/symptom_analysis/possible_disease', methods=['GET', 'POST'])
def possible_disease():
    # Get data from user input and get the possible disease from db
    user_input_symptom = request.args.getlist('user_input_symptom')
    selected = 'symptom'
    possible_diseases_db = []
    for i in range(len(user_input_symptom)):
        disease_names_query = table.DiseaseAndSymptom.query.filter_by(symptom=user_input_symptom[i]).all()
        for disease_name_query in disease_names_query:
            possible_diseases_db.append(disease_name_query.disease_name)

    return render_template('features/possible_disease.html', selected=selected,
                           user_input_symptom=user_input_symptom,
                           possible_diseases_db=list(set(possible_diseases_db)))


@app.route('/symptom_analysis/possible_disease/<disease>/desc')
def disease_desc(disease):
    selected = 'desc'
    user_input_disease = disease
    desc = table.DiseaseAndDesc.query.filter_by(disease_name=user_input_disease).first()
    treatments_query = table.DiseaseAndTreatment.query.filter_by(disease_name=user_input_disease).all()
    preventions_query = table.DiseaseAndPrevention.query.filter_by(disease_name=user_input_disease).all()
    img_query = table.DiseaseAndImg.query.filter_by(disease_name=user_input_disease).all()

    return render_template('features/disease_desc.html', selected=selected,
                           desc=desc.desc,
                           treatments_query=treatments_query,
                           preventions_query=preventions_query,
                           img_query=img_query,
                           user_input_disease=user_input_disease)


# ---------------------End of Symptom Analysis------------------------


# ---------------------Nutrition--------------------------------------


@app.route("/nutrition")
def nutrition():
    """Get the data from db into db

    Returns:
        template: /features/nutrition.html
        contents and author query
    """

    selected = 'nutrition'
    info_source = 'https://www.msdvetmanual.com/management-and-nutrition/nutrition-pigs/nutritional-requirements-of' \
                  '-pigs'
    author = table.AuthorNutritionInfo.query.all()
    contents = table.MainNutritionInfo.query.all()
    return render_template("/features/nutrition.html", selected=selected,
                           contents=contents,
                           info_source=info_source,
                           author=author)


# ---------------------End of Nutrition-------------------------------


# ---------------------Facts------------------------------------------


@app.route("/facts")
def facts():
    """Get the data from db into Front End

    Returns:
        template: /features/facts.html
        data facts and facts_resume query
    """
    selected = 'facts'
    facts_query = table.FactsAboutPigs.query.all()[3:]
    facts_resume = table.FactsAboutPigs.query.all()[:3]

    # facts origin url, index 0
    # facts_resume origin url, index 1

    urls = ['https://www.coolkidfacts.com/facts-about-pigs/',
            'https://kids.nationalgeographic.com/animals/mammals/facts/pig']

    return render_template("/features/facts.html", selected=selected,
                           facts=facts_query,
                           facts_resume=facts_resume,
                           urls=urls,)


# ---------------------End of Types-----------------------------------

# ---------------------Types------------------------------------------


@app.route("/types")
def types():
    """Get 6 common types in db, display it in Front-end

    Returns:
        template: /features/types.html
        data: 6 common types query
    """
    selected = 'types'
    twenty_types = table.TypesOfPigs.query.all()
    common_types = [twenty_types[0], twenty_types[1], twenty_types[2],
                    twenty_types[5], twenty_types[7], twenty_types[17]]

    return render_template("/features/types.html", selected=selected,
                           common_types=common_types)


# ---------------------End of Types-----------------------------------


# ---------------------Calender---------------------------------------

# Future update: use celery to handle the asych To delay the sending of an email in Celery, you can use the
# apply_async() method with the countdown or eta parameter. The countdown parameter specifies the number of seconds
# to wait before executing the task, while the eta parameter specifies the exact date and time to execute the task

class GetUserInfo(FlaskForm):
    date_field = DateField('Insemination Date: ', validators=[DataRequired()])
    email_field = EmailField('Enter Email: ', validators=[DataRequired(), Email()])
    submit_field = SubmitField('Submit')


@app.route("/calendar")
def calendar():
    """Display information (hardcoded) about due date of pigs

    Returns:
        template: /features/calendar.html
    """

    selected = 'calendar'
    info_source = 'https://www.roysfarm.com/raising-pigs/'
    return render_template("/features/calendar.html", selected=selected,
                           info_source=info_source)


@app.route("/calendar/send_emails", methods=['GET', 'POST'])
def send_mail():
    """Prepare the emails to be sent

    Returns:
        template: /features/send_mail.html
        data: form
    """
    selected = 'calendar'
    form = GetUserInfo()
    due_date = None
    if form.validate_on_submit():
        date = form.date_field.data
        email = form.email_field.data
        print(date, email)
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

        my_thread = threading.Thread(target=send_emails, args=(email, date))
        # Create a new thread

        # Start the new thread
        my_thread.start()
        form.date_field.data = ''
        form.email_field.data = ''
    return render_template("/features/send_mail.html", selected=selected,
                           form=form,
                           due_date=due_date)


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

    # ------------------------------------------------------------------------------------
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


# ---------------------End of Calender-----------------------------------


# ---------------------News----------------------------------------------


@app.route("/news")
def news():
    """Get news from db and show it in Front end

    Returns:
        template: /features/news.html
        data: dbarticles and dbnews(query)
    """
    selected = 'news'

    dbarticles = table.ScrapedNews.query.filter_by(type='article').all()
    dbnews = table.ScrapedNews.query.filter_by(type='news').all()

    db.session.commit()

    return render_template("/features/news.html",  selected=selected,
                           dbarticles=dbarticles,
                           dbnews=dbnews)


@app.route("/news/scrape-news")
def scrape_news():
    """On windows load in news, update the news card UI

    Returns:
        template: /features/scrape_news.html
        data: dbarticles and dbnews(scraped and query it)
    """
    selected = 'news'
    today = datetime.today()

    dbdate = db.session.query(table.ScrapedNews.date).first()
    datetime_object = datetime.strptime(dbdate[0], "%B %d, %Y")
    # Check if url of the website being scraped is working.
    try:
        urls = ['https://www.swineweb.com/', 'https://www.thepigsite.com/']

        for url in urls:
            response = requests.get(url)
            doc = BeautifulSoup(response.content, "html.parser")
            # Updates the scraped articles
            if url == urls[0]:
                articles = doc.css.select('div.td_module_14 ')
                dbarticles = table.ScrapedNews.query.filter_by(type='article').all()

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
                dbnews_all = table.ScrapedNews.query.filter_by(type='news').all()

                # Loop the scrape news 3 times and update db
                for counter in range(3):
                    news_div = news_divs[counter]
                    link = news_div.css.select_one('div.article-summary-title a')
                    date_text = news_div.css.select_one('span.align-items-center').text.strip()
                    format_date = date_text.split()

                    title = news_div.css.select_one('div.article-summary-title').text.strip()
                    date = format_date[1] + ' ' + format_date[0] + ", " + format_date[2]
                    desc = news_div.css.select_one('div.article-summary-text').text.strip() + '...'
                    img_url = news_div.css.select_one('a.article-summary-image img').get('src')
                    a = link.get('href')

                    dbnews = dbnews_all[counter]
                    dbnews.title = title
                    dbnews.date = date
                    dbnews.desc = desc
                    dbnews.a = a
                    dbnews.img_url = img_url
                    db.session.commit()

        dbarticles = table.ScrapedNews.query.filter_by(type='article').all()
        dbnews = table.ScrapedNews.query.filter_by(type='news').all()
        db.session.commit()

        return render_template("/features/scrape_news.html", dbnews=dbnews, dbarticles=dbarticles, selected=selected)

    except requests.exceptions.ConnectionError:

        dbarticles = table.ScrapedNews.query.filter_by(type='article').all()
        dbnews = table.ScrapedNews.query.filter_by(type='news').all()

        db.session.commit()

        return render_template("/features/news.html", dbnews=dbnews, dbarticles=dbarticles, selected=selected)


# ---------------------End of News---------------------------------------


# ---------------------Prices--------------------------------------------


class Refresh(FlaskForm):
    refresh = SubmitField('Refresh')


@app.route("/price")
def price():
    """Get the prices from db and pass it in UI

    Return:
        template: /features/price.html
        data: prices from db
    """

    selected = 'price'

    form = Refresh()

    if form.validate_on_submit():
        flash('Scraping for prices')
        return redirect(url_for('price_scrape'))

    pork_with_bones = table.Prices.query.filter_by(type='pork_with_bones').first()
    live_weight = table.Prices.query.filter_by(type='live_weight').first()
    pork_kasim = table.Prices.query.filter_by(type='pork_kasim').first()

    return render_template("/features/price.html", selected=selected,
                           pork_with_bones=pork_with_bones,
                           live_weight=live_weight,
                           pork_kasim=pork_kasim,
                           form=form)


# Refresh button to scrape again the sites, and save in db. insert sql
@app.route('/price/refresh', methods=['POST', 'GET'])
def price_scrape():
    """On refresh click this will run, scraping prices and updating UI

    Returns:
        template: /features/price.html
        data: prices from internet
    """

    selected = 'price'

    form = Refresh()

    pork_with_bones = table.Prices.query.filter_by(type='pork_with_bones').first()
    live_weight = table.Prices.query.filter_by(type='live_weight').first()
    pork_kasim = table.Prices.query.filter_by(type='pork_kasim').first()

    urls = [
        'https://www.ceicdata.com/en/philippines/retail-price-selected-agricultural-commodities/retail-price-pork'
        '-with-bones-region-4a-batangas-city',
        'https://psa.gov.ph/livestock-poultry-iprs/swine/prices?fbclid'
        '=IwAR00Bu7aWKomFUmsuoMwD5SIMTKzxLGsn4YQNQsGlTFOmzv5sp8r0HzwacU',
        'https://www.ceicdata.com/en/philippines/retail-price-selected-agricultural-commodities/retail-price-pork'
        '-kasim-region-3-central-luzon']

    for url in urls:
        # Checkk if url of the website being scraped is working.
        try:
            response = requests.get(url)
            doc = BeautifulSoup(response.content, "html.parser")
        except requests.exceptions.ConnectionError:
            flash('The website that provides informtion have problem....')
            return render_template("/features/price.html", selected=selected,
                                   form=None,
                                   pork_with_bones=pork_with_bones,
                                   live_weight=live_weight,
                                   pork_kasim=pork_kasim)

            # Pork with Bones price scrape
        if url == urls[0]:
            table_element = doc.table
            tr = table_element.findAll('tr')
            span = tr[1].findAll('span')
            num = tr[1].span.text.strip()
            price_with_peso = '₱ ' + num
            pork_with_bones.price = price_with_peso

            query = table.Prices.query.filter_by(type='pork_with_bones').first()
            query.price = price_with_peso

        # Live weight price scrape
        if url == urls[1]:
            def extract_numbers(string_with_num):
                find_numbers = re.findall(r'\d+', string_with_num)
                number = '.'.join(find_numbers)

                return '₱ ' + number

            div = doc.find('div')
            span = div.css.select('span.nowrap')
            price_with_peso = extract_numbers(span[0].text)
            live_weight.price = price_with_peso

            query = table.Prices.query.filter_by(type='live_weight').first()
            query.price = price_with_peso

        if url == urls[2]:
            table_element = doc.table
            tr = table_element.findAll('tr')
            span = tr[1].findAll('span')
            num = tr[1].span.text.strip()
            price_with_peso = '₱ ' + num

            pork_kasim.price = price_with_peso
            query = table.Prices.query.filter_by(type='pork_kasim').first()
            query.price = price_with_peso

    db.session.commit()

    return render_template("/features/price.html", selected=selected,
                           form=form,
                           pork_with_bones=pork_with_bones,
                           live_weight=live_weight,
                           pork_kasim=pork_kasim)

# ---------------------End of Prices-----------------------------------------
