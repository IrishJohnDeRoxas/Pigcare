from bs4 import BeautifulSoup
import sqlalchemy as db
import requests, re
from sqlalchemy.orm import sessionmaker   

engine = db.create_engine('mysql+pymysql://root:Biboy_321@localhost/pigcare')
Session = sessionmaker(bind=engine)
session = Session()

from sqlalchemy.orm import declarative_base
db.Model = declarative_base()

# Define a model for the table
class author_nutrition_info(db.Model):
    __tablename__ = 'author_nutrition_info' # Change the table name
    id = db.Column(db.Integer, primary_key=True)
    title =  db.Column (db.String(500) ,nullable= False)
    author =  db.Column (db.String(500) ,nullable= False)
    author_desc =  db.Column (db.String(500) ,nullable= False)
    
# Define a model for the table
class main_nutrition_info(db.Model):
    __tablename__ = 'main_nutrition_info' # Change the table name
    id = db.Column(db.Integer, primary_key=True)
    header =  db.Column (db.String(300) ,nullable= False)
    desc = db.Column(db.Text(16383), nullable=False)
    
# Define a model for the table
class sub_nutrition_info(db.Model):
    __tablename__ = 'sub_nutrition_info' # Change the table name
    id = db.Column(db.Integer, primary_key=True)
    sub_header =  db.Column (db.String(300) ,nullable= False)
    sub_desc = db.Column(db.String(5000), nullable=False)
    
# Create the table if it doesn't exist
db.Model.metadata.create_all(engine)

url = 'https://www.msdvetmanual.com/management-and-nutrition/nutrition-pigs/nutritional-requirements-of-pigs'

response = requests.get(url)
doc = BeautifulSoup(response.content, 'html.parser')


title = doc.css.select_one('h1.topic__header__headermodify--title').text.strip()
author = doc.css.select_one('strong.topic__label').text
author_desc= doc.css.select('p.topic__authors--description')[1].text

# Adding the title, author and author_desc in db
author_info_entry = author_nutrition_info(title=title, author=author, author_desc=author_desc)
# session.add(author_info_entry)

topic_sections = doc.css.select('section.topic__section')
topic_sections.pop()
# print(topic_sections[-2].text)

headers = doc.css.select('h2.topic__header--section')
headers_text = [header.text.strip() for header in headers]

desc_text = []
for topic_section in topic_sections:
    main_header = topic_section.css.select('h2.topic__header--section')
    for header in main_header:
        # print(header.text)
        pass
    desc_text.append(topic_section.text.replace(header.text, ''))

    
sub_contents = doc.css.select('section.GHead ')

sub_headers = doc.css.select('h3.topic__header--subsection')
sub_headers_text = [sub_header.text.strip() for sub_header in sub_headers]

sub_desc_text = []
for sub_content in sub_contents:
    sub_headers = sub_content.css.select('h3.topic__header--subsection')
    for sub_header in sub_headers:
        pass
  
    sub_desc_text.append(sub_content.text.replace(sub_header.text.strip(), ''))

# Adding the main content into db
for i in range(len(headers_text)):
    main_nutrition_info_entry = main_nutrition_info(header = headers_text[i], desc = desc_text[i])
#     session.add(main_nutrition_info_entry)
#     session.commit()

# Adding the sub content into db
for i in range(len(sub_headers_text)):
    sub_nutrition_info_entry = sub_nutrition_info(sub_header = sub_headers_text[i], 
                                                  sub_desc = sub_desc_text[i])
#     session.add(sub_nutrition_info_entry)
#     session.commit()

# session.commit()
