import sqlalchemy as db
from werkzeug.security import generate_password_hash
from sqlalchemy.orm import sessionmaker   

engine = db.create_engine('mysql+pymysql://root:Biboy_321@localhost/pigcare')
Session = sessionmaker(bind=engine)
session = Session()

from sqlalchemy.orm import declarative_base
db.Model = declarative_base()

class admin(db.Model):
    __tablename__ = 'admin' # Change the table name
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column (db.Text(), nullable=False)
    password = db.Column (db.Text(), nullable=False)
    
# hashed_pwd = generate_password_hash('admin', 'sha256')

# entry = admin(username='admin', password = hashed_pwd)
# session.add(entry)
# session.commit()