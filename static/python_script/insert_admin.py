import sqlalchemy as db
from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy.orm import sessionmaker   

engine = db.create_engine('mysql+pymysql://root:Biboy_321@localhost/pigcare2')
Session = sessionmaker(bind=engine)
session = Session()

from sqlalchemy.orm import declarative_base
db.Model = declarative_base()

class AdminModel(db.Model):
    __tablename__ = 'admin'  # Change the table name
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.VARCHAR(255), nullable=False, unique=True)
    hashed_password = db.Column(db.TEXT(), nullable=False)

    
# hashed_pwd = generate_password_hash('admin')

# entry = AdminModel(username='admin', hashed_password = hashed_pwd)
# session.add(entry)
# session.commit()