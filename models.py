from config import db, generate_password_hash, check_password_hash, UserMixin

# ---------------------------------------------Admin DB Tables----------------------------------------------------------


class AdminModel(db.Model, UserMixin):
    __tablename__ = 'admin'  # Change the table name
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.VARCHAR(255), nullable=False, unique=True)
    hashed_password = db.Column(db.TEXT(), nullable=False)

    @property
    def password(self):
        raise AttributeError('Password is not readable')

    @password.setter
    def password(self, password):
        self.hashed_password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.hashed_password, password)
    
    
# ----------------------------------------End of Admin DB Tables-------------------------------------------------------- 
    
# --------------------------------------Symptom Analysis DB Tables------------------------------------------------------


class Diseases(db.Model):
    __tablename__ = 'diseases'  # Change the table name
    dn_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.VARCHAR(255), unique=True)
    desc = db.Column(db.TEXT())
    
    symptom = db.relationship('DiseaseAndSymptom', backref='diseases_and_symptom', )
    prevention = db.relationship('DiseaseAndPrevention', backref='disease_and_prevention')
    treatment = db.relationship('DiseaseAndTreatment', backref='disease_and_treatment')
    img = db.relationship('DiseaseAndImg', backref='disease_and_img')


class Symptoms(db.Model):
    __tablename__ = 'symptoms'  # Change the table name
    s_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.VARCHAR(255), unique=True) 
       
    symptoms = db.relationship('DiseaseAndSymptom', backref = 'disease_and_symptoms', )
    
    
class Preventions(db.Model):
    __tablename__ = 'preventions'  # Change the table name
    P_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    prevention = db.Column(db.VARCHAR(255), unique=True)
    
    disease = db.relationship('DiseaseAndPrevention', backref = 'disease_and_preventions')
    

class DiseaseAndSymptom(db.Model):
    __tablename__ = 'disease_and_symptom'  # Change the table name
    ds_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symptom = db.Column(db.VARCHAR(255), db.ForeignKey('symptoms.name', ondelete='CASCADE', onupdate='CASCADE'))
    disease = db.Column(db.VARCHAR(255), db.ForeignKey('diseases.name', ondelete='CASCADE', onupdate='CASCADE'))
    
    
class DiseaseAndPrevention(db.Model):
    __tablename__ = 'disease_and_prevention'  # Change the table name
    dp_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    disease = db.Column(db.VARCHAR(255), db.ForeignKey('diseases.name', ondelete='CASCADE', onupdate='CASCADE'))
    prevention = db.Column(db.VARCHAR(255), db.ForeignKey('preventions.prevention', ondelete='CASCADE', onupdate='CASCADE'))


class DiseaseAndTreatment(db.Model):
    __tablename__ = 'disease_and_treatment'  # Change the table name
    dt_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    disease = db.Column(db.VARCHAR(255), db.ForeignKey('diseases.name', ondelete='CASCADE', onupdate='CASCADE'))
    treatment = db.Column(db.TEXT())


class DiseaseAndImg(db.Model):
    __tablename__ = 'disease_and_img'  # Change the table name
    di_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    disease = db.Column(db.VARCHAR(255), db.ForeignKey('diseases.name', ondelete='CASCADE', onupdate='CASCADE'))
    img = db.Column(db.TEXT(), nullable=False)
    img_credits = db.Column(db.TEXT())


# --------------------------------------End of Symptom Analysis DB Tables-----------------------------------------------

# ------------------------------------------Post Content DB Tables------------------------------------------------------


class PostContent(db.Model):
    __tablename__ = 'post_content'  # Change the table name
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.VARCHAR(255), nullable=False)
    author = db.Column(db.VARCHAR(255), nullable=False)
    header = db.Column(db.VARCHAR(255), nullable=False)
    desc = db.Column(db.Text(), nullable=False)
    source = db.Column(db.Text())
    date = db.Column(db.Text())
    img = db.Column(db.Text())
    img_credits = db.Column(db.Text())


# ----------------------------------------End of Post Content DB Tables-------------------------------------------------


# ------------------------------------------------News DB Tables--------------------------------------------------------


class ScrapedNews(db.Model):
    __tablename__ = 'scraped_news'  # Change the table name
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.VARCHAR(250), nullable=False)
    title = db.Column(db.VARCHAR(250), nullable=False)
    date = db.Column(db.VARCHAR(250), nullable=False)
    desc = db.Column(db.VARCHAR(400), nullable=False)
    a = db.Column(db.VARCHAR(1500), nullable=False)
    img_url = db.Column(db.VARCHAR(1500), nullable=False)


# -----------------------------------------------End of News DB Tables--------------------------------------------------


# ------------------------------------------------Prices DB Tables------------------------------------------------------


class Prices(db.Model):
    __tablename__ = 'prices'  # Change the table name
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.VARCHAR(250), nullable=False)
    price = db.Column(db.VARCHAR(250), nullable=False)
    date_of_price = db.Column(db.VARCHAR(250), nullable=False)
    header = db.Column(db.VARCHAR(150), nullable=False)
    a = db.Column(db.VARCHAR(150), nullable=False)
    href = db.Column(db.VARCHAR(1000), nullable=False)


# -----------------------------------------------End of Prices DB Tables------------------------------------------------

