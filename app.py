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
from config import app, db, login_user, LoginManager, login_required, logout_user,\
        check_password_hash, secure_filename, render_template, request, redirect, \
        url_for, flash, session
from bs4 import BeautifulSoup
from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.fields import DateField, EmailField, SelectMultipleField, StringField,\
    PasswordField, TextAreaField, SelectField, RadioField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired, Email, ValidationError
from wtforms.widgets import CheckboxInput, ListWidget, RadioInput
import uuid as uuid
import utils
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
    return table.AdminModel.query.get(int(user_id))


if __name__ == '__main__':
    app.run(debug=True)


@app.route("/")
def index():
    # Render the template with the page name as an argument
    return render_template("features/base/index.html")


# --------------------- Admin ----------------------------------------

class AdminLoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired()])
    password = PasswordField('Password',
                             validators=[DataRequired()])
    submit = SubmitField('Sign In')


class ContentForm(FlaskForm):
    author = StringField('Author', validators=[DataRequired()])
    header = StringField('Header', validators=[DataRequired()])
    desc = TextAreaField('Description', validators=[DataRequired()])
    source = TextAreaField('Source of information', validators=[])
    date = StringField('Date', validators=[])
    image = FileField(label='Image',
                      validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    img_credits = StringField('Image credits', validators=[])
    
    clear = SubmitField('Clear Form')
    add_image = SubmitField('Add image')
    
    submit_all = SubmitField('Submit')
    save_edit = SubmitField('Save')
    

@app.route('/admin/delete/<post_id>', methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    post_to_delete = table.PostContent.query.filter_by(id=post_id).first()
    filename = post_to_delete.img
    
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    except FileNotFoundError as e:
        print(e)
    except TypeError as e:
        print(e)
    
    table.PostContent.query.filter_by(id=post_id).delete()
    db.session.commit()
    
    flash ('Deleted a post')
    return redirect(request.referrer)


@app.route('/admin/edit/delete/<image_filename>/', methods=['GET', 'POST'])
@login_required
def delete_image(image_filename):
    form = ContentForm()
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
    except FileNotFoundError:
        print(f"File '{image_filename}' doesn't exist in upload folder.")
    
    if 'content_form_data' in session:
        session['content_form_data']['image_filename'] = None
        session['content_form_data']['image_credits'] = None
    
    check_img_db = table.PostContent.query.filter_by(img=image_filename).first()
        
    if check_img_db:
        check_img_db.img = None
        check_img_db.img_credits = None
        
        db.session.commit()

    flash('Deleted Successfully')
    return redirect(request.referrer)


@app.route("/admin/login", methods=['GET', 'POST'])
def login():
    selected = 'login'
    form = AdminLoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        admin_creds = table.AdminModel.query.filter_by(username=username).first()

        if admin_creds:
            if check_password_hash(admin_creds.hashed_password, password):
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


# --------------------- Symptom Analysis Admin -----------------------


class AdminSymptomAnalysisForm(FlaskForm):
    
    symptoms = RadioField(label='Symptoms', )
    symptoms_choice = TextAreaField(label='Add Possible Symptoms',
                                  validators=[]) 
    
    disease = StringField(label='Disease',
                           validators=[DataRequired()])
    desc = TextAreaField(label='Description',
                           validators=[DataRequired()])
    
    treatments = RadioField(label='Treatment', )
    treatments_choice = TextAreaField(label='Add Possible Treatments',
                                    validators=[]) 
    
    preventions = RadioField(label='Prevention', )
    preventions_choice = TextAreaField(label='Add Possible Preventions',
                                    validators=[]) 
    image = FileField(label='Image',
                validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    img_credits = StringField('Image Source',
                           validators=[])
    
    add_symptom_choice = SubmitField('Add symptom')
    add_treatment_choice = SubmitField('Add treatment')
    add_prevention_choice = SubmitField('Add prevention')
    add_image = SubmitField('Add image')
    
    edit_symptom_choice = SubmitField('Edit symptom')
    edit_treatment_choice = SubmitField('Edit treatment')
    edit_prevention_choice = SubmitField('Edit prevention')
    
    delete_symptom_choice = SubmitField('Delete symptom')
    delete_treatment_choice = SubmitField('Delete treatment')
    delete_prevention_choice = SubmitField('Delete prevention')
    
    # Submit all data 
    submit_all = SubmitField('Submit')
    
    # Save for edit function 
    save_edit = SubmitField('Save')
    
    clear = SubmitField('Clear')


@app.route('/admin/symptom', methods=['GET', 'POST'])
@login_required
def admin_symptom():
    selected = 'admin_symptom'
    diseases = table.Diseases.query.all()
    form = AdminSymptomAnalysisForm()
    
    form.disease.data = ''  
    form.desc.data = '' 
    form.img_credits.data = '' 
    form.symptoms.choices = ''
    form.treatments.choices = ''
    form.preventions.choices = ''
    form.symptoms_choice.data = ''
    form.treatments_choice.data = ''
    form.preventions_choice.data = ''     
    utils.disease_name.clear()
    utils.desc.clear()                                             
    utils.current_values_symptom.clear()
    utils.current_values_treatment.clear()
    utils.current_values_prevention.clear()
    utils.image_filenames.clear()
    utils.image_credits.clear()
    session.pop('form_data', None) 
    
    return render_template('admin/control/symptom/admin_symptom.html', selected=selected,
                           diseases=diseases)

@app.before_request
def store_symptom_form_data():
    if request.endpoint == 'admin_add_symptom' or request.endpoint == 'admin_edit_symptom':        
        form = AdminSymptomAnalysisForm()
        
        if request.method == 'POST':
            session['form_data'] = {
                'disease': form.disease.data,
                'desc': form.desc.data,
                'image_filenames': utils.image_filenames,                       
                'image_credits': utils.image_credits,                       
                'symptom_choices': utils.current_values_symptom,                       
                'treatment_choices':  utils.current_values_treatment,                       
                'prevention_choices':  utils.current_values_prevention,                       
            }   
    
@app.route('/admin/symptom/add', methods=['GET', 'POST'])
@login_required
def admin_add_symptom():
    selected = 'admin_symptom'       
    form = AdminSymptomAnalysisForm()
    
    # Populate the form after deleting
    if utils.disease_name:
        form.disease.data = utils.disease_name[0]
        form.desc.data = utils.desc[0]
    if utils.current_values_symptom:
        form.symptoms.choices = utils.current_values_symptom
    if utils.current_values_prevention:
        form.preventions.choices = utils.current_values_prevention
    if utils.current_values_treatment:
        form.treatments.choices = utils.current_values_treatment
        
    if request.method == 'POST':  
        
        if 'form_data' in session:        
            form.disease.data = session['form_data']['disease']
            form.desc.data = session['form_data']['desc'] 
            form.symptoms.choices = session['form_data']['symptom_choices']
            form.treatments.choices = session['form_data']['treatment_choices']
            form.preventions.choices = session['form_data']['prevention_choices']
            session.pop('form_data', None) 

        try:
            if utils.symptom_analysis_form_buttons(form):            
                flash('Saved Success')
                selected = 'admin_symptom'
                diseases = table.Diseases.query.all()            
                return render_template('admin/control/symptom/admin_symptom.html', selected=selected,
                           diseases=diseases)
        except ValueError as e:
            flash(f"Error saving data: {str(e)}")
            form.disease.data = '' 
            selected = 'admin_symptom'
            diseases = table.Diseases.query.all()            
            return redirect(url_for('admin_symptom', selected=selected,diseases=diseases))        
            
    image_filenames=utils.image_filenames
    image_credits=utils.image_credits
    filename_credits_dict = dict(zip(image_filenames,image_credits))
    return render_template('admin/control/symptom/admin_add_symptom.html', selected=selected,
                        form=form,
                        image_filenames=image_filenames,
                        filename_credits_dict=filename_credits_dict)   


@app.route('/admin/symptom/edit/<disease>', methods=['GET', 'POST'])
@login_required
def admin_edit_symptom(disease):
    selected = 'admin_symptom'
    form = AdminSymptomAnalysisForm()
    if 'form_data' in session:        
        form.disease.data = session['form_data']['disease']
        form.desc.data = session['form_data']['desc'] 
        form.symptoms.choices = session['form_data']['symptom_choices']
        form.treatments.choices = session['form_data']['treatment_choices']
        form.preventions.choices = session['form_data']['prevention_choices']
        session.pop('form_data', None) 
    else:        
    
        disease_value = table.Diseases.query.filter_by(name=disease).first()    
        image_values = table.DiseaseAndImg.query.filter_by(disease=disease)   
            
        symptom_values = table.DiseaseAndSymptom.query.filter_by(disease=disease)
        treatment_values = table.DiseaseAndTreatment.query.filter_by(disease=disease)
        prevention_values = table.DiseaseAndPrevention.query.filter_by(disease=disease)
        
        symptom_choices = [symptom_value.symptom for symptom_value in symptom_values]
        treatment_choice = [treatment_value.treatment for treatment_value in treatment_values]
        prevention_choice = [prevention_value.prevention for prevention_value in prevention_values]
        
        utils.current_values_symptom.extend(symptom_choices)
        utils.current_values_treatment.extend(treatment_choice)
        utils.current_values_prevention.extend(prevention_choice)
        
        for image_value in image_values:
            utils.image_filenames.append(image_value.img)            
            utils.image_credits.append(image_value.img_credits)            
        
        form.disease.data = disease_value.name  
        form.desc.data = disease_value.desc
        form.img_credits.data = utils.image_credits[0]
        form.symptoms.choices = list(set(utils.current_values_symptom))
        form.treatments.choices = list(set(utils.current_values_treatment))
        form.preventions.choices = list(set(utils.current_values_prevention))
        
    if request.method == 'POST':  
        if utils.symptom_analysis_form_buttons(form):
            flash('Edited Successfully')
            selected = 'admin_symptom'
            diseases = table.Diseases.query.all()            
            return redirect(url_for('admin_symptom', selected=selected,diseases=diseases))
    
    image_filenames=utils.image_filenames
    image_credits=utils.image_credits
    filename_credits_dict = dict(zip(image_filenames,image_credits))      
    return render_template('admin/control/symptom/admin_edit_symptom.html', selected=selected,
                        form=form,                           
                        image_filenames=image_filenames,
                        filename_credits_dict=filename_credits_dict)
   
        
@app.route('/admin/symptom/edit/delete/<filename>/<filename_credits_dict>', methods=['GET', 'POST'])
@login_required
def delete_image_symptom(filename,filename_credits_dict):

    # Delete image in add symptom form
    if url_for('admin_add_symptom') in request.referrer:
        
        formatted_dict = eval(filename_credits_dict)    
        image_credits = formatted_dict[filename] 
        
        utils.image_filenames.remove(filename)  
        utils.image_credits.remove(image_credits)
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('Deleted Successfully')
        return redirect(request.referrer)
    
    # Delete image in edit symptom form
    if url_for('admin_edit_symptom', disease='') in request.referrer:
        
        formatted_dict = eval(filename_credits_dict)    
        image_credits = formatted_dict[filename] 
        
        table.DiseaseAndImg.query.filter_by(img=filename).delete()
        db.session.commit()
        
        utils.image_filenames.remove(filename)  
        utils.image_credits.remove(image_credits)
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('Deleted Successfully')
        return redirect(request.referrer)


@app.route('/admin/symptom/edit/delete/<disease>', methods=['GET', 'POST'])
@login_required
def delete_disease(disease):
    table.Diseases.query.filter_by(name=disease).delete()
    db.session.commit()
    flash(f'{disease} deleted')
    return redirect(request.referrer)

# --------------------- End of Symptom Analysis Admin ----------------


# --------------------------- Nutrition Admin ------------------------


@app.route('/admin/nutrition', methods=['GET', 'POST'])
@login_required
def admin_nutrition():
    selected = 'admin_nutrition'
    form = ContentForm()
    utils.clear_content_form(form)
    nutritions = table.PostContent.query.filter_by(type='nutrition').all()
    return render_template('admin/control/nutrition/admin_nutrition.html', selected=selected,
                           form=form,
                           nutritions=nutritions)

@app.route('/admin/nutrition/add', methods=['GET', 'POST'])
@login_required
def admin_add_nutrition():
    selected = 'admin_nutrition'
    form = ContentForm()
    
    if 'content_form_data' in session:
        utils.populate_content_form(form)
        
    if request.method == 'POST':
        if utils.content_form(form):
            return redirect(url_for('admin_nutrition'))
            # utils.populate_content_form(form)
    
    if 'content_form_data' in session:
        image_filename = session['content_form_data']['image_filename']
        
        return render_template('admin/control/nutrition/admin_add_nutrition.html', selected=selected,
                                form=form,
                                image_filename=image_filename)
        
    return render_template('admin/control/nutrition/admin_add_nutrition.html', selected=selected,
                           form=form)

@app.route('/admin/nutrition/edit/', methods=['GET', 'POST'])
@login_required
def admin_edit_nutrition():
    post_id =  request.args.get('post_id')
    selected = 'admin_nutrition'
    form = ContentForm()
    
    if not form.author.data:
        utils.populate_edit_content_form(form, post_id)
        
    if request.method == 'POST':
        if utils.content_form(form):
            flash("Post edited successfully!", "success")
            return redirect(url_for('admin_nutrition'))
    
    if 'content_form_data' in session:
        image_filename = session['content_form_data']['image_filename']
        
        return render_template('admin/control/nutrition/admin_edit_nutrition.html', selected=selected,
                                form=form,
                                image_filename=image_filename)
    
    content = table.PostContent.query.filter_by(id=post_id).first()
    image_filename=content.img
    print(image_filename)
    return render_template('admin/control/nutrition/admin_edit_nutrition.html', selected=selected,
                            form=form,
                            image_filename=image_filename)
        

# ----------------------- End of Nutrition Admin ---------------------


# ---------------------------- Admin Facts ---------------------------

@app.route('/admin/facts', methods=['GET', 'POST'])
@login_required
def admin_facts():
    selected = 'admin_facts'
    form = ContentForm()
    utils.clear_content_form(form)
    facts = table.PostContent.query.filter_by(type='facts').all()
    return render_template('admin/control/facts/admin_facts.html', selected=selected,
                           form=form,
                           facts=facts)

@app.route('/admin/facts/add', methods=['GET', 'POST'])
@login_required
def admin_add_facts():
    selected = 'admin_facts'
    form = ContentForm()
    
    if 'content_form_data' in session:
        utils.populate_content_form(form)
        
    if request.method == 'POST':
        if utils.content_form(form):
            return redirect(url_for('admin_facts'))
            # utils.populate_content_form(form)
    
    if 'content_form_data' in session:
        image_filename = session['content_form_data']['image_filename']
        
        return render_template('admin/control/facts/admin_add_facts.html', selected=selected,
                                form=form,
                                image_filename=image_filename)
        
    return render_template('admin/control/facts/admin_add_facts.html', selected=selected,
                            form=form,)

@app.route('/admin/facts/edit/', methods=['GET', 'POST'])
@login_required
def admin_edit_facts():
    post_id =  request.args.get('post_id')
    selected = 'admin_facts'
    form = ContentForm()
    
    if not form.author.data:
        utils.populate_edit_content_form(form, post_id)
        
    if request.method == 'POST':
        if utils.content_form(form):
            flash("Post edited successfully!", "success")
            return redirect(url_for('admin_facts'))
    
    if 'content_form_data' in session:
        image_filename = session['content_form_data']['image_filename']
        
        return render_template('admin/control/facts/admin_edit_facts.html', selected=selected,
                                form=form,
                                image_filename=image_filename)
    
    content = table.PostContent.query.filter_by(id=post_id).first()
    image_filename=content.img
    print(image_filename)
    return render_template('admin/control/facts/admin_edit_facts.html', selected=selected,
                            form=form,
                            image_filename=image_filename)


# ------------------------- End of Admin Facts -----------------------


# ---------------------------- Admin Types ---------------------------

@app.route('/admin/types', methods=['GET', 'POST'])
@login_required
def admin_types():
    selected = 'admin_types'
    form = ContentForm()
    utils.clear_content_form(form)
    types_db = table.PostContent.query.filter_by(type='type_of_pig').all()
    return render_template('admin/control/types/admin_types.html', selected=selected,
                           form=form,
                           types_db=types_db)
    
@app.route('/admin/types/add', methods=['GET', 'POST'])
@login_required
def admin_add_types():
    selected = 'admin_types'
    form = ContentForm()
    
    if 'content_form_data' in session:
        utils.populate_content_form(form)
        
    if request.method == 'POST':
        if utils.content_form(form):
            return redirect(url_for('admin_types'))
            # utils.populate_content_form(form)
    
    if 'content_form_data' in session:
        image_filename = session['content_form_data']['image_filename']
        
        return render_template('admin/control/types/admin_add_types.html', selected=selected,
                                form=form,
                                image_filename=image_filename)
        
    return render_template('admin/control/types/admin_add_types.html', selected=selected,
                            form=form,)

@app.route('/admin/types/edit/', methods=['GET', 'POST'])
@login_required
def admin_edit_types():
    post_id =  request.args.get('post_id')
    selected = 'admin_types'
    form = ContentForm()
    
    if not form.author.data:
        utils.populate_edit_content_form(form, post_id)
        
    if request.method == 'POST':
        if utils.content_form(form):
            flash("Post edited successfully!", "success")
            return redirect(url_for('admin_types'))
    
    if 'content_form_data' in session:
        image_filename = session['content_form_data']['image_filename']
        
        return render_template('admin/control/types/admin_edit_types.html', selected=selected,
                                form=form,
                                image_filename=image_filename)
    
    content = table.PostContent.query.filter_by(id=post_id).first()
    image_filename=content.img
    print(image_filename)
    return render_template('admin/control/types/admin_edit_types.html', selected=selected,
                            form=form,
                            image_filename=image_filename)

# ------------------------- End of Admin Types -----------------------


# --------------------------- Admin Calendar -------------------------

@app.route('/admin/simulate-calendar', methods=['GET', 'POST'])
@login_required
def admin_calendar():
    selected = 'admin_calendar'
    form = ContentForm()
    utils.clear_content_form(form)
    simulate_calendar = table.PostContent.query.filter_by(type='simulate_calendar').all()
    return render_template('admin/control/calendar/admin_calendar.html', selected=selected,
                           form=form,
                           simulate_calendar=simulate_calendar)

@app.route('/admin/calendar/add', methods=['GET', 'POST'])
@login_required
def admin_add_calendar():
    selected = 'admin_calendar'
    form = ContentForm()
    
    if 'content_form_data' in session:
        utils.populate_content_form(form)
        
    if request.method == 'POST':
        if utils.content_form(form):
            return redirect(url_for('admin_calendar'))
            # utils.populate_content_form(form)
    
    if 'content_form_data' in session:
        image_filename = session['content_form_data']['image_filename']
        
        return render_template('admin/control/calendar/admin_add_calendar.html', selected=selected,
                                form=form,
                                image_filename=image_filename)
        
    return render_template('admin/control/calendar/admin_add_calendar.html', selected=selected,
                            form=form,)

@app.route('/admin/calendar/edit/', methods=['GET', 'POST'])
@login_required
def admin_edit_calendar():
    post_id =  request.args.get('post_id')
    selected = 'admin_calendar'
    form = ContentForm()
    
    if not form.author.data:
        utils.populate_edit_content_form(form, post_id)
        
    if request.method == 'POST':
        if utils.content_form(form):
            flash("Post edited successfully!", "success")
            return redirect(url_for('admin_calendar'))
    
    if 'content_form_data' in session:
        image_filename = session['content_form_data']['image_filename']
        
        return render_template('admin/control/calendar/admin_edit_calendar.html', selected=selected,
                                form=form,
                                image_filename=image_filename)
    
    content = table.PostContent.query.filter_by(id=post_id).first()
    image_filename=content.img
    print(image_filename)
    return render_template('admin/control/calendar/admin_edit_calendar.html', selected=selected,
                            form=form,
                            image_filename=image_filename)

# ------------------------ End of Admin Calendar ---------------------


# ---------------------------- Admin News ----------------------------

@app.route('/admin/news', methods=['GET', 'POST'])
@login_required
def admin_news():
    selected = 'admin_news'
    form = ContentForm()
    utils.clear_content_form(form)
    articles = table.PostContent.query.filter_by(type='news').all()
    return render_template('admin/control/news/admin_news.html', selected=selected,
                           form=form,
                           articles=articles)
    
@app.route('/admin/news/add', methods=['GET', 'POST'])
@login_required
def admin_add_news():
    selected = 'admin_news'
    form = ContentForm()
    
    if 'content_form_data' in session:
        utils.populate_content_form(form)
        
    if request.method == 'POST':
        if utils.content_form(form):
            return redirect(url_for('admin_news'))
    
    if 'content_form_data' in session:
        image_filename = session['content_form_data']['image_filename']
        
        return render_template('admin/control/news/admin_add_news.html', selected=selected,
                                form=form,
                                image_filename=image_filename)
        
    return render_template('admin/control/news/admin_add_news.html', selected=selected,
                            form=form,)

@app.route('/admin/news/edit/', methods=['GET', 'POST'])
@login_required
def admin_edit_news():
    post_id =  request.args.get('post_id')
    selected = 'admin_news'
    form = ContentForm()
    
    if not form.author.data:
        utils.populate_edit_content_form(form, post_id)
        
    if request.method == 'POST':
        if utils.content_form(form):
            flash("Post edited successfully!", "success")
            return redirect(url_for('admin_news'))
    
    if 'content_form_data' in session:
        image_filename = session['content_form_data']['image_filename']
        
        return render_template('admin/control/news/admin_edit_news.html', selected=selected,
                                form=form,
                                image_filename=image_filename)
    
    content = table.PostContent.query.filter_by(id=post_id).first()
    image_filename=content.img
    print(image_filename)
    return render_template('admin/control/news/admin_edit_news.html', selected=selected,
                            form=form,
                            image_filename=image_filename)

# -------------------------- End of Admin News -----------------------


# --------------------------- Admin Price ----------------------------

@app.route('/admin/price', methods=['GET', 'POST'])
@login_required
def admin_price():
    selected = 'admin_price'
    pork_with_bones = table.Prices.query.filter_by(type='pork_with_bones').first()
    live_weight = table.Prices.query.filter_by(type='live_weight').first()
    pork_kasim = table.Prices.query.filter_by(type='pork_kasim').first()
    return render_template('admin/control/price/admin_price.html', selected=selected,
                           pork_with_bones=pork_with_bones,
                           live_weight=live_weight,
                           pork_kasim=pork_kasim)

# -------------------------- End of Admin Price ----------------------


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


@app.route('/symptom_analysis', methods=['GET', 'POST'])
def symptom_analysis():
    # Get user input symptom, process it into possible disease
    selected = 'symptom'
    form = SymptomForm()
    choices_db = table.Symptoms.query.all()
    choices = [choice.name for choice in choices_db]
    form.symptoms_field.choices = choices
    possible_disease_query = table.Diseases.query.all()
    possible_diseases_db = [disease.name for disease in possible_disease_query]
    disease_img_query = table.DiseaseAndImg.query.all()
    if form.validate_on_submit():
        user_input_symptom = request.form.getlist('symptoms_field')
        return redirect(url_for('possible_disease',
                                user_input_symptom=user_input_symptom,
                                selected=selected))

    return render_template('features/symptom_analysis.html', selected=selected,
                           form=form,
                           disease_img_query= disease_img_query)


@app.route('/symptom_analysis/possible_disease', methods=['GET', 'POST'])
def possible_disease():
    # Get data from user input and get the possible disease from db
    user_input_symptom = request.args.getlist('user_input_symptom')
    selected = 'symptom'
    possible_diseases_db = []
    for i in range(len(user_input_symptom)):
        disease_names_query = table.DiseaseAndSymptom.query.filter_by(symptom=user_input_symptom[i]).all()
        for disease_name_query in disease_names_query:
            possible_diseases_db.append(disease_name_query.disease)

    return render_template('features/possible_disease.html', selected=selected,
                           user_input_symptom=user_input_symptom,
                           possible_diseases_db=list(set(possible_diseases_db)))


@app.route('/symptom_analysis/possible_disease/<disease>/desc')
def disease_desc(disease):
    selected = 'desc'
    user_input_disease = disease
    desc = table.Diseases.query.filter_by(name=user_input_disease).first()
    treatments_query = table.DiseaseAndTreatment.query.filter_by(disease=user_input_disease).all()
    preventions_query = table.DiseaseAndPrevention.query.filter_by(disease=user_input_disease).all()
    img_query = table.DiseaseAndImg.query.filter_by(disease=user_input_disease).all()

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
    
    nutrition_posts = table.PostContent.query.filter_by(type='nutrition').all()
    return render_template("/features/nutrition.html", selected=selected,
                           nutrition_posts=nutrition_posts)


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
    fact_posts = table.PostContent.query.filter_by(type='facts').all()

    return render_template("/features/facts.html", selected=selected,
                           fact_posts=fact_posts)


# ---------------------End of Types-----------------------------------

# ---------------------Types------------------------------------------


@app.route("/types")
def types():

    selected = 'types'
    type_posts = table.PostContent.query.filter_by(type='type_of_pig').all()

    return render_template("/features/types.html", selected=selected,
                           type_posts=type_posts)


# ---------------------End of Types-----------------------------------


# ---------------------Calender---------------------------------------

# Future update: use celery to handle the asych To delay the sending of an email in Celery, you can use the
# apply_async() method with the countdown or eta parameter. The countdown parameter specifies the number of seconds
# to wait before executing the task, while the eta parameter specifies the exact date and time to execute the task

class GetUserInfo(FlaskForm):
    date_field = DateField('Insemination Date: ', validators=[DataRequired()])
    email_field = EmailField('Enter Email: ', validators=[DataRequired(), Email()])
    submit_field = SubmitField('Submit')


class SimulateCalendarForm(FlaskForm):
    information = StringField('Simulate Calendar Information', validators=[DataRequired()])
    submit_field = SubmitField('Submit')



@app.route("/calendar")
def calendar():
    selected = 'calendar'
    simulate_calendar_posts = table.PostContent.query.filter_by(type='simulate_calendar').all()
    return render_template("/features/calendar.html", selected=selected,
                           simulate_calendar_posts=simulate_calendar_posts)


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

@app.route("/news/")
def news():
    """On windows load in news, update the news card UI

    Returns:
        template: /features/news.html
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

        admin_news_posts = table.PostContent.query.filter_by(type='news').all() 
        
        return render_template("/features/news.html",selected=selected,
                               dbnews=dbnews,
                               dbarticles=dbarticles,
                               admin_news_posts=admin_news_posts)

    except requests.exceptions.ConnectionError:

        dbarticles = table.ScrapedNews.query.filter_by(type='article').all()
        dbnews = table.ScrapedNews.query.filter_by(type='news').all()

        db.session.commit()

        return render_template("/features/news.html", dbnews=dbnews, dbarticles=dbarticles, selected=selected)


# ---------------------End of News---------------------------------------


# ---------------------Prices--------------------------------------------


@app.route("/price")
def price():
    """Get the prices from db and pass it in UI

    Return:
        template: /features/price.html
        data: prices from db
    """

    selected = 'price'

    pork_with_bones = table.Prices.query.filter_by(type='pork_with_bones').first()
    live_weight = table.Prices.query.filter_by(type='live_weight').first()
    pork_kasim = table.Prices.query.filter_by(type='pork_kasim').first()

    return render_template("/features/price.html", selected=selected,
                           pork_with_bones=pork_with_bones,
                           live_weight=live_weight,
                           pork_kasim=pork_kasim,)


# Refresh button to scrape again the sites, and save in db. insert sql
@app.route('/admin/price/refresh', methods=['POST', 'GET'])
def price_scrape():

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
            return redirect(request.referrer)

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
            db.session.commit()

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
            db.session.commit()

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

    
    flash('Refresh successfully')
    return redirect(request.referrer)

# ---------------------End of Prices-----------------------------------------
