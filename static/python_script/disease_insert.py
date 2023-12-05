import sqlalchemy as db
import requests, re, json, os
from sqlalchemy.orm import sessionmaker   

engine = db.create_engine('mysql+pymysql://root:Biboy_321@localhost/pigcare')
Session = sessionmaker(bind=engine)
session = Session()

from sqlalchemy.orm import declarative_base
db.Model = declarative_base()

current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)

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
    DT_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    disease_name =  db.Column (db.VARCHAR(255))
    treatment = db.Column (db.TEXT())

class disease_and_img(db.Model):
    __tablename__ = 'disease_and_img' # Change the table name
    DI_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    disease_name =  db.Column (db.VARCHAR(255))
    img = db.Column (db.TEXT())
    source = db.Column (db.TEXT())
    
def insert_name(values):
    
    for value in values:
        try:
            name_entry = disease_name(name=value)
            session.add(name_entry)
        except db.exc.IntegrityError:
            # Skip duplicate records and continue processing
            print(f"Duplicate key found for symptom: {value}")
            continue
    session.commit() 
    
def insert_symptom(values):
    for value in values:
        print(value)
        try:
            symptom_entry = symptoms(symptom=value)
            session.add(symptom_entry)
        except db.exc.IntegrityError:
            continue
    session.commit()

def insert_prevention(values):
    for value in values:
        try:
            prevention_entry = preventions(prevention=value)
            session.add(prevention_entry)
        except db.exc.IntegrityError:
            print(f"Duplicate key found for symptom: {value}")
            continue
    session.commit()

def insert_DN_S(DN, S):
    for i in range(len(S)):
        DN_S_entry = disease_and_symptom(disease_name= DN, symptom=S[i])
        session.add(DN_S_entry)
    session.commit()
    
def insert_DN_P(DN, P):    
    if P == None:
        DN_P_entry = disease_and_prevention(disease_name= DN, prevention=None)
        session.add(DN_P_entry)
    else:
        for i in range(len(P)):    
            DN_P_entry = disease_and_prevention(disease_name= DN, prevention=P[i])
            session.add(DN_P_entry)
    session.commit()
    
def insert_DN_D(DN, D):
    DN_D_entry = disease_and_desc(disease_name = DN, desc = D)
    session.add(DN_D_entry)
    session.commit()

def insert_DN_T(DN, T):  
    # print(DN, T, "\n")  
    if T == None:
        DN_T_entry = disease_and_treatment(disease_name= DN, treatment=T)
        session.add(DN_T_entry)
    else:
        for i in range(len(T)):  
            DN_T_entry = disease_and_treatment(disease_name= DN, treatment=T[i])
            session.add(DN_T_entry)
        
    session.commit()

def insert_DN_I(DN, img, src):
        # print(DN, T, "\n")  
    if src == None :
        for i in range(len(img)):  
            DN_I_entry = disease_and_img(disease_name= DN, img=img[i], source=src)
            session.add(DN_I_entry)
    else:
        for i in range(len(img)):  
            DN_I_entry = disease_and_img(disease_name= DN, img=img[i] ,source=src[i])
            session.add(DN_I_entry)
        
    session.commit()
    
with open(parent_dir+"\json\pig_disease.json") as f:
    data = json.load(f)
    disease_names_list = []
    symptoms_list = []
    prevention_list = []
    
    # print(f"{disease_name_json} {symptoms_json} ")
    for i in range(len(data['disease'])):    
        object = data['disease'][i]
        
        disease_name_json = object['name'].strip()
        symptoms_json = object['symptoms']
        preventions_json = object['preventions']
        desc_json = object['desc']
        treatment_json = object['treatment']
        img_json = object['image']
        src_img_json = object['image_source']
        
        disease_names_list.append(disease_name_json)
        
        for symptom in symptoms_json:
            symptoms_list.append(symptom)
            
        if preventions_json:    
            for prevention in preventions_json:
                prevention_list.append(prevention)
            
        # insert_DN_S(disease_name_json,symptoms_json)    
        # insert_DN_P(disease_name_json,preventions_json)
        # insert_DN_D(disease_name_json,desc_json)
        # insert_DN_T(disease_name_json,treatment_json)
        # insert_DN_I(disease_name_json,img_json,src_img_json)
                
    final_symptoms_list = list(set(symptoms_list))
    final_preventions_list = list(set(prevention_list))
    
    # insert_name(disease_names_list)
    # insert_symptom(final_symptoms_list)
    # insert_prevention(final_preventions_list)
    