from config import db

# --------------------------------------Symptom Analysis DB Tables------------------------------------------------------


class DiseaseName(db.Model):
    __tablename__ = 'disease_name'  # Change the table name
    DN_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.VARCHAR(255), unique=True)


class Symptoms(db.Model):
    __tablename__ = 'symptoms'  # Change the table name
    S_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symptom = db.Column(db.VARCHAR(255), unique=True)


class Preventions(db.Model):
    __tablename__ = 'preventions'  # Change the table name
    P_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    prevention = db.Column(db.VARCHAR(255), unique=True)


class DiseaseAndSymptom(db.Model):
    __tablename__ = 'disease_and_symptom'  # Change the table name
    DS_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    disease_name = db.Column(db.VARCHAR(255), nullable=False, unique=True)
    symptom = db.Column(db.VARCHAR(255))


class DiseaseAndPrevention(db.Model):
    __tablename__ = 'disease_and_prevention'  # Change the table name
    DP_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    disease_name = db.Column(db.VARCHAR(255), nullable=False, unique=True)
    prevention = db.Column(db.VARCHAR(255))


class DiseaseAndDesc(db.Model):
    __tablename__ = 'disease_and_desc'  # Change the table name
    DD_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    disease_name = db.Column(db.VARCHAR(255))
    desc = db.Column(db.TEXT())


class DiseaseAndTreatment(db.Model):
    __tablename__ = 'disease_and_treatment'  # Change the table name
    Dt_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    disease_name = db.Column(db.VARCHAR(255))
    treatment = db.Column(db.TEXT())


class DiseaseAndImg(db.Model):
    __tablename__ = 'disease_and_img'  # Change the table name
    DI_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    disease_name = db.Column(db.VARCHAR(255))
    img = db.Column(db.TEXT())
    source = db.Column(db.TEXT())


# --------------------------------------End of Symptom Analysis DB Tables-----------------------------------------------

# ---------------------------------------------Nutrition DB Tables------------------------------------------------------


class AuthorNutritionInfo(db.Model):
    __tablename__ = 'author_nutrition_info'  # Change the table name
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    author = db.Column(db.String(500), nullable=False)
    author_desc = db.Column(db.String(500), nullable=False)


class MainNutritionInfo(db.Model):
    __tablename__ = 'main_nutrition_info'  # Change the table name
    id = db.Column(db.Integer, primary_key=True)
    header = db.Column(db.String(300), nullable=False)
    desc = db.Column(db.Text(16383), nullable=False)


class SubNutritionInfo(db.Model):
    __tablename__ = 'sub_nutrition_info'  # Change the table name
    id = db.Column(db.Integer, primary_key=True)
    sub_header = db.Column(db.String(300), nullable=False)
    sub_desc = db.Column(db.String(5000), nullable=False)


# ----------------------------------------End of Nutrition DB Tables----------------------------------------------------

# ---------------------------------------------Facts DB Tables----------------------------------------------------------


class FactsAboutPigs(db.Model):
    __tablename__ = 'facts_about_pigs'  # Change the table name
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    desc = db.Column(db.String(2000), nullable=False)


# ---------------------------------------------End of Facts DB Tables---------------------------------------------------

# ---------------------------------------------Types DB Tables----------------------------------------------------------


class TypesOfPigs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    desc = db.Column(db.String(1500), nullable=False)
    a = db.Column(db.String(1500), nullable=False)
    img_url = db.Column(db.String(1500), nullable=False)


# ---------------------------------------------End of Types DB Tables---------------------------------------------------

# ------------------------------------------------News DB Tables--------------------------------------------------------


class ScrapedNews(db.Model):
    __tablename__ = 'scraped_news'  # Change the table name
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(250), nullable=False)
    title = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    desc = db.Column(db.String(400), nullable=False)
    a = db.Column(db.String(1500), nullable=False)
    img_url = db.Column(db.String(1500), nullable=False)


# -----------------------------------------------End of News DB Tables--------------------------------------------------


# ------------------------------------------------Prices DB Tables------------------------------------------------------


class Prices(db.Model):
    __tablename__ = 'prices'  # Change the table name
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(250), nullable=False)
    price = db.Column(db.String(250), nullable=False)
    date_of_price = db.Column(db.String(250), nullable=False)
    header = db.Column(db.String(150), nullable=False)
    a = db.Column(db.String(150), nullable=False)
    href = db.Column(db.String(1000), nullable=False)


# -----------------------------------------------End of Prices DB Tables------------------------------------------------

