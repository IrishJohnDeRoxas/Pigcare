from bs4 import BeautifulSoup
import sqlalchemy, requests, re
from sqlalchemy.orm import sessionmaker   

engine = sqlalchemy.create_engine('mysql+pymysql://root:Biboy_321@localhost/pigcare')
Session = sessionmaker(bind=engine)
session = Session()

from sqlalchemy.orm import declarative_base
Base = declarative_base()


# Define a model for the table
class types_of_pigs(Base):
    __tablename__ = 'types_of_pigs'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    title =  sqlalchemy.Column (sqlalchemy.String(250) ,nullable= False)
    desc = sqlalchemy.Column(sqlalchemy.String(1500), nullable=False)
    a = sqlalchemy.Column(sqlalchemy.String(1500), nullable=False)
    img_url = sqlalchemy.Column(sqlalchemy.String(1500), nullable=False)
    
# Create the table if it doesn't exist
Base.metadata.create_all(engine)

url = 'https://farmerdb.com/types-of-pigs/?fbclid=IwAR0gdDtYDZf48ELE03TGSKzllOlVLpvu40kxnMSf0UXSlVHeGdVKRxGFnN0'

response = requests.get(url)
doc = BeautifulSoup(response.content, 'html.parser')

content_div = doc.css.select_one('div.entry-content')
titles = content_div.find_all('h2')

final_titles = [re.sub(r"\d+", "", title.text).replace('. ', '') for title in titles[:20]]
descs = content_div.css.select('p.bc')

images = content_div.css.select('img.size-full')
links = []

for image in images:
    link = image.get('src')
    links.append(link)
    
all_jpg_links = [link for link in links if link.endswith('.jpg')]
links_to_remove = ['https://farmerdb.com/wp-content/uploads/2023/04/Types-Of-Pigs-Pig-breeds.jpg',
                    'https://farmerdb.com/wp-content/uploads/2023/04/Duroc-Pig-Farming-Guide.jpg',
                    'https://farmerdb.com/wp-content/uploads/2023/04/Discover-Everything-You-Need-to-Know-About-Mangalica-Pigs.jpg',
                    'https://farmerdb.com/wp-content/uploads/2023/04/Raising-American-Guinea-Hog.jpg',
                    'https://farmerdb.com/wp-content/uploads/2023/04/Everything-about-Hereford-Pigs.jpg',
                    'https://farmerdb.com/wp-content/uploads/2023/04/Raising-Kunekune-Pigs-on-a-Farm.jpg',
                    'https://farmerdb.com/wp-content/uploads/2023/04/What-to-consider-when-choosing-a-type-of-pig.jpg',
                    'https://farmerdb.com/wp-content/uploads/2023/04/Pig-breeding-concept.jpg',
                    'https://farmerdb.com/wp-content/uploads/2023/04/Pig-breeding.jpg',]

final_jpg_links = [link for link in all_jpg_links if link not in links_to_remove]
    

for i in range(20):
    new_row = types_of_pigs(title = final_titles[i], desc = descs[i].text, a = url, img_url = final_jpg_links[i])
    # session.add(new_row)
    # session.commit()