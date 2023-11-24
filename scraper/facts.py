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
class facts_about_pigs(db.Model):
    __tablename__ = 'facts_about_pigs' # Change the table name
    id = db.Column(db.Integer, primary_key=True)
    title =  db.Column (db.String(300) ,nullable= False)
    desc = db.Column(db.String(2000), nullable=False)
    
# Create the table if it doesn't exist
db.Model.metadata.create_all(engine)

urls = ['https://kids.nationalgeographic.com/animals/mammals/facts/pig', 'https://www.coolkidfacts.com/facts-about-pigs/']


for url in urls:
    if url == urls[0]:
        response = requests.get(url)
        doc = BeautifulSoup(response.content, 'html.parser')
        
        facts_div = doc.css.select('div.FastFacts__TopFacts__Data')
        
        facts = [facts_div[i].text for i in range(3) ]
        
        for fact in facts:
            title_and_desc_list = re.split(r':\s+', fact)
            title = title_and_desc_list[0]
            desc = title_and_desc_list[1]
            new_row = facts_about_pigs(title=title, desc=desc)
            session.add(new_row)
            session.commit()
    
    if url == urls[1]:
        response = requests.get(url)
        doc = BeautifulSoup(response.content, 'html.parser')
        
        titles = doc.css.select('h3.wp-block-heading')
        
        def format_titles(title):
            remove_numbers = re.sub(r'\d+', '', title)
            return remove_numbers.replace('#', '').replace('.', '').strip()
        
        titles_list = [format_titles(titles[i].text) for i in range(6)]
        
        desc_list = [titles[i].find_next('p').text for i in range(6)]
        
        for i in range(6):
            new_row = facts_about_pigs(title = titles_list[i], desc = desc_list[i])
            session.add(new_row)
            session.commit()
    