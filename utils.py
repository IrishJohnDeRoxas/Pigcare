from config import app, db, login_user, LoginManager, login_required, logout_user,\
        check_password_hash, secure_filename, render_template, request, redirect, \
        url_for, flash, session
import models as table
import os
import uuid as uuid

disease_name = []
desc = []
image_filenames = [] 
image_credits = []      
current_values_symptom = [] 
current_values_treatment = [] 
current_values_prevention = [] 
selected = 'admin_symptom'

def symptom_analysis_form_buttons(form):
    if request.form.get('clear'):
        # Clear all fields    
        
        form.disease.data = ''  
        form.desc.data = '' 
        form.img_credits.data = '' 
        form.symptoms.choices = ''
        form.treatments.choices = ''
        form.preventions.choices = ''
        form.symptoms_choice.data = ''
        form.treatments_choice.data = ''
        form.preventions_choice.data = ''                                                  
        current_values_symptom.clear()
        current_values_treatment.clear()
        current_values_prevention.clear()
        image_filenames.clear()
        image_credits.clear()
        session.pop('form_data', None) 
                
    # User populate the select field with symptom choice
    elif request.form.get('add_symptom_choice') and form.symptoms_choice.data:     
        
        if form.symptoms_choice.data.title() not in form.symptoms.choices :
            current_values_symptom.append(form.symptoms_choice.data.title())                
            form.symptoms.choices = list(set(current_values_symptom))
            form.treatments.choices = list(set(current_values_treatment))
            form.preventions.choices = list(set(current_values_prevention))
            form.symptoms_choice.data = ''
        else:
            flash(f'{form.symptoms_choice.data.title()} is already in choices')   
            form.symptoms_choice.data = ''
    
    # User populate the select field with treatments
    elif request.form.get('add_treatment_choice') and form.treatments_choice.data:   
        
        if form.treatments_choice.data.title() not in form.treatments.choices:
            current_values_treatment.append(form.treatments_choice.data.title())
            form.symptoms.choices = list(set(current_values_symptom))
            form.treatments.choices = list(set(current_values_treatment))
            form.preventions.choices = list(set(current_values_prevention))
            form.treatments_choice.data = ''   
        else:
            flash(f'{form.treatments_choice.data.title()} is already in choices')   
            form.treatments_choice.data = ''
    
    # User populate the select field with prevetions
    elif request.form.get('add_prevention_choice') and form.preventions_choice.data:  
        
        if form.preventions_choice.data.title() not in form.preventions.choices:                          
            current_values_prevention.append(form.preventions_choice.data.title())
            form.symptoms.choices = list(set(current_values_symptom))
            form.treatments.choices = list(set(current_values_treatment))
            form.preventions.choices = list(set(current_values_prevention))
            form.preventions_choice.data = ''  
        else:
            flash(f'{form.preventions_choice.data.title()} is already in choices')   
            form.preventions_choice.data = ''  
    
    # User add a image and display it
    elif request.form.get('add_image') and request.files['image']:
        image = request.files['image']
        filename = secure_filename(image.filename)        
        unique_filename = str(uuid.uuid1()) + '_' + filename   
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))        
        image_filenames.append(unique_filename)        
        image_credits.append(form.img_credits.data)
        
        form.symptoms.choices = list(set(current_values_symptom))
        form.treatments.choices = list(set(current_values_treatment))
        form.preventions.choices = list(set(current_values_prevention)) 
        
        disease_name.append(form.disease.data)
        desc.append(form.desc.data)
        
        session['form_data'] = {
                'disease': form.disease.data,
                'desc': form.desc.data,
                'image_filenames': image_filenames,                       
                'image_credits': image_credits,                       
                'symptom_choices': current_values_symptom,                       
                'treatment_choices':  current_values_treatment,                       
                'prevention_choices':  current_values_prevention,                       
            }  
                   
        form.img_credits.data = ''
    
    elif request.form.get('edit_symptom_choice'):
        # Check if there is selected symptom
        if form.symptoms.data:
            form.symptoms_choice.data = form.symptoms.data
            current_values_symptom.remove(form.symptoms.data)
        else:
            flash('Please select a symptom to edit')
            
    elif request.form.get('edit_treatment_choice'):
        # Check if there is selected treatment
        if form.treatments.data:
            form.treatments_choice.data = form.treatments.data
            current_values_treatment.remove(form.treatments.data)
            
        else:
            flash('Please select a treatment to edit')
            
    elif request.form.get('edit_prevention_choice'):
        # Check if there is selected treatment
        if form.preventions.data:
            form.preventions_choice.data = form.preventions.data
            current_values_prevention.remove(form.preventions.data)
                
        else:
            flash('Please select a prevention to edit')
    
    elif request.form.get('delete_symptom_choice'):
        if form.symptoms.data:
            current_values_symptom.remove(form.symptoms.data)    
            form.symptoms.choices = current_values_symptom    
            symptom_to_delete = table.DiseaseAndSymptom.query.filter_by(symptom=form.symptoms.data).first()
            if symptom_to_delete:
                db.session.delete(symptom_to_delete)
                db.session.commit()
            flash('Deleted a symptom')
        else:
            flash('Please select a symptom to delete')
    
    elif request.form.get('delete_treatment_choice'):
        if form.treatments.data:
            current_values_treatment.remove(form.treatments.data)    
            form.treatments.choices = current_values_treatment    
            treatment_to_delete = table.DiseaseAndTreatment.query.filter_by(treatment=form.treatments.data).first()
            if treatment_to_delete:
                db.session.delete(treatment_to_delete)
                db.session.commit()
            flash('Deleted a treatment')
        else:
            flash('Please select a treatment to delete')
            
    elif request.form.get('delete_prevention_choice'):
        if form.preventions.data:
            current_values_prevention.remove(form.preventions.data)    
            form.preventions.choices = current_values_prevention    
            prevention_to_delete = table.DiseaseAndPrevention.query.filter_by(prevention=form.preventions.data).first()
            if prevention_to_delete:
                db.session.delete(prevention_to_delete)
                db.session.commit()
            flash('Deleted a prevention')
        else:
            flash('Please select a prevention to delete')
                        
    # When everything is populated, check for error                                  
    elif request.form.get('submit_all'):
        # Handle error when symptoms, treatment 
        if current_values_symptom == []:
            flash('input symptom')
        elif current_values_treatment == []:
            form.symptoms.choices = list(set(current_values_symptom))
            flash('input treatment')
        else:        
            # Check if the disease already exists                
            disease_table = table.Diseases.query.filter_by(name=form.disease.data).first()            
            if disease_table:                
                # Delete the images in directory 
                for img in image_filenames:                    
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], img))
                    image_filenames.remove(img)
                
                # Clear cache
                current_values_symptom.clear()
                current_values_treatment.clear()
                current_values_prevention.clear()   
                image_filenames.clear()
                form.desc.data = ''
                               
                raise ValueError (f'{form.disease.data} is already in database')               
            # If disease do not exist yet insert into db             
            else:
                # Insert Disease only           
                disease_entry = table.Diseases(name=form.disease.data, desc=form.desc.data)
                db.session.add(disease_entry)
                db.session.commit()
                                            
                # Insert Symptom only
                for symptom in set(current_values_symptom):
                    existing_symptom = table.Symptoms.query.filter_by(name=symptom).first()
                    if not existing_symptom:
                        new_symptom = table.Symptoms(name=symptom)
                        db.session.add(new_symptom)
                        db.session.commit()

                # Insert Prevention only                            
                for prevention in set(current_values_prevention):
                    existing_prevention = table.Preventions.query.filter_by(prevention=prevention).first()
                    if not existing_prevention:
                        new_prevention = table.Preventions(prevention=prevention)
                        db.session.add(new_prevention)
                    db.session.commit()
                
                # Insert Disease and symptom 
                for symptom in list(set(current_values_symptom)):                    
                    ds_entry = table.DiseaseAndSymptom(symptom=symptom, disease=form.disease.data)  
                    db.session.add(ds_entry)
                    db.session.commit()
                    
                # Insert Disease and prevention
                for prevention in list(set(current_values_prevention)):
                    dp_entry = table.DiseaseAndPrevention(disease=form.disease.data, prevention=prevention)  
                    db.session.add(dp_entry)
                    db.session.commit()
                    
                # Insert Disease and treatment 
                for treatment in list(set(current_values_treatment)):
                    dt_entry = table.DiseaseAndTreatment(disease=form.disease.data, treatment=treatment)  
                    db.session.add(dt_entry)
                    db.session.commit()  

                # Insert Disease and image 
                for i in range(len(image_filenames)):
                    di_entry = table.DiseaseAndImg(disease=form.disease.data, img=image_filenames[i], img_credits=image_credits[i])
                    db.session.add(di_entry)
                    db.session.commit()
                            
                # Clear cache   
                
                session.pop('form_data', None)                             
                current_values_symptom.clear()
                current_values_treatment.clear()
                current_values_prevention.clear()
                image_filenames.clear()
                image_credits.clear()
                form.disease.data = ''  
                form.desc.data = ''  
                
                selected = 'admin_symptom'
                diseases = table.Diseases.query.all() 
                flash('Saved Successfully')           
                return redirect(url_for('admin_symptom', selected=selected,diseases=diseases))
                
    
    elif request.form.get('save_edit'):
        # Save edited data         
        disease_table = table.Diseases.query.filter_by(name=form.disease.data).first() 
        disease_to_update = table.Diseases.query.get(disease_table.dn_id)
        disease_to_update.name = form.disease.data     
        disease_to_update.desc = form.desc.data     
        db.session.commit()           
        
        
        # Delete old data
        table.DiseaseAndSymptom.query.filter_by(disease=form.disease.data).delete()
        db.session.commit()
        
        table.DiseaseAndPrevention.query.filter_by(disease=form.disease.data).delete()
        db.session.commit()
        
        table.DiseaseAndTreatment.query.filter_by(disease=form.disease.data).delete()
        db.session.commit()
        
        table.DiseaseAndImg.query.filter_by(disease=form.disease.data).delete()
        db.session.commit()
        
         # Insert Symptom only
        for symptom in set(current_values_symptom):
            existing_symptom = table.Symptoms.query.filter_by(name=symptom).first()
            if not existing_symptom:
                new_symptom = table.Symptoms(name=symptom)
                db.session.add(new_symptom)
                db.session.commit()

        # Insert Prevention only                            
        for prevention in set(current_values_prevention):
            existing_prevention = table.Preventions.query.filter_by(prevention=prevention).first()
            if not existing_prevention:
                new_prevention = table.Preventions(prevention=prevention)
                db.session.add(new_prevention)
            db.session.commit()
        
        # Insert Disease and symptom 
        for symptom in set(form.symptoms.choices):
            # Check for db for duplicate combination                           
            ds_entry = table.DiseaseAndSymptom(symptom=symptom, disease=form.disease.data)  
            db.session.add(ds_entry)
            db.session.commit()
        
        # Insert Disease and prevention
        for prevention in form.preventions.choices:
            dp_entry = table.DiseaseAndPrevention(disease=form.disease.data, prevention=prevention)  
            db.session.add(dp_entry)
            db.session.commit()
        
        # Insert Disease and treatment 
        for treatment in form.treatments.choices:
            dt_entry = table.DiseaseAndTreatment(disease=form.disease.data, treatment=treatment)  
            db.session.add(dt_entry)
            db.session.commit()  

        # Insert Disease and image 
        for i in range(len(image_filenames)):
            di_entry = table.DiseaseAndImg(disease=form.disease.data, img=image_filenames[i], img_credits=image_credits[i])
            db.session.add(di_entry)
            db.session.commit()
                    
        # Clear cache     
        session.pop('form_data', None)                             
        current_values_symptom.clear()
        current_values_treatment.clear()
        current_values_prevention.clear()
        image_filenames.clear()
        image_credits.clear()
        form.disease.data = ''  
        form.desc.data = ''  
        
        selected = 'admin_symptom'
        diseases = table.Diseases.query.all()
        return render_template('admin/control/admin_symptom.html', selected=selected,
                           diseases=diseases)
    
    else:
        flash('Cannot add an empty field to choices')
        form.symptoms.choices = list(set(current_values_symptom))
        form.treatments.choices = list(set(current_values_treatment))
        form.preventions.choices = list(set(current_values_prevention))                    
        return render_template('admin/control/symptom/admin_add_symptom.html', selected='admin_symptom', 
                                form=form,
                                image_filenames=image_filenames)    


def populate_content_form(form): 
    form.author.data = session['content_form_data']['author']
    form.header.data = session['content_form_data']['header']
    form.desc.data = session['content_form_data']['desc']
    form.source.data = session['content_form_data']['source']
    form.date.data = session['content_form_data']['date']

def populate_edit_content_form(form, post_id):
    content = table.PostContent.query.filter_by(id=post_id).first()
    form.author.data = content.author
    form.header.data = content.header
    form.desc.data = content.desc
    form.source.data = content.source
    form.date.data = content.date
    if content.img:
        image_filenames.append(content.img)
        image_credits.append(content.img_credits)
        
def clear_content_form(form):
    form.author.data = ''
    form.header.data = ''
    form.desc.data = ''
    form.source.data = '' 
    form.img_credits.data = ''   
    form.date.data = ''  
    session.pop('content_form_data', None) 

def content_form(form):
    
    if request.form.get('clear'):
        if 'content_form_data'in session:
            filename = session['content_form_data']['image_filename']
            if filename:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                except FileNotFoundError:
                    print(f"File '{filename}' doesn't exist in upload folder.")
                
        clear_content_form(form)
        
    
    elif request.form.get('add_image') and request.files['image']:
        
        post_id = request.args.get('post_id')
        if 'content_form_data' in session:
            if session['content_form_data']['image_filename']:            
                form.img_credits.data = ''
                flash('Can only add one image')
            
        elif post_id: # Edit content form, only one image is allowed
            check_img_db = table.PostContent.query.filter_by(id=post_id).first()
            if check_img_db.img:
                form.img_credits.data = ''
                flash('Can only add one image')
            
            image = request.files['image']
            filename = secure_filename(image.filename)        
            unique_filename = str(uuid.uuid1()) + '_' + filename   
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))   
               
            session['content_form_data'] = {
                'author': form.author.data,
                'header': form.header.data,
                'desc': form.desc.data, 
                'source': form.source.data,
                'date': form.date.data,
                'image_filename': unique_filename,                       
                'image_credits': form.img_credits.data,                                             
            }  
            
            form.img_credits.data = ''
            populate_content_form(form)
                
        else: # Add content form, only one image is allowed
            image = request.files['image']
            filename = secure_filename(image.filename)        
            unique_filename = str(uuid.uuid1()) + '_' + filename   
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))   
               
            session['content_form_data'] = {
                'author': form.author.data,
                'header': form.header.data,
                'desc': form.desc.data, 
                'source': form.source.data,
                'date': form.date.data,
                'image_filename': unique_filename,                       
                'image_credits': form.img_credits.data,                                             
            }  
            
            form.img_credits.data = ''
            populate_content_form(form)
            
    # When everything is populated, check for error                                  
    elif request.form.get('submit_all'):
        
        # Insert into post_content from nutrition
        if url_for('admin_add_nutrition') in request.referrer:
            type = 'nutrition'
            message = 'Added a Nutrition Post'
            
        if url_for('admin_add_facts') in request.referrer:
            type = 'facts'
            message = 'Added a Fact Post'
            
        if url_for('admin_add_types') in request.referrer:
            type = 'type_of_pig'
            message = 'Added a new type'
            
        if url_for('admin_add_news') in request.referrer:
            type = 'news'
            message = 'Added a new article'
            
        if url_for('admin_add_calendar') in request.referrer:
            type = 'simulate_calendar'
            message = 'Added a new information about swine preganancy'
            
        if session.get('content_form_data'):    
            post_entry = table.PostContent(type=type,
                                           author=session['content_form_data']['author'],
                                           header=session['content_form_data']['header'], 
                                           desc=session['content_form_data']['desc'],
                                           source=session['content_form_data']['source'],
                                           date=session['content_form_data']['date'],
                                           img=session['content_form_data']['image_filename'],
                                           img_credits=session['content_form_data']['image_credits'])
            
            clear_content_form(form)
            
            db.session.add(post_entry)
            db.session.commit()
            flash(f'{message}')
            return redirect(request.referrer)
        else:
            post_entry = table.PostContent(type=type,
                                author=form.author.data,
                                header=form.header.data, 
                                desc=form.desc.data,
                                source=form.source.data,
                                date=form.date.data,)
            
            clear_content_form(form)
            
            db.session.add(post_entry)
            db.session.commit()
            flash(f'{message}')
            return redirect(request.referrer)

    elif request.form.get('save_edit'):
        #save all data
        post_id = request.args.get('post_id')
        content_to_update = table.PostContent.query.filter_by(id=post_id).first()
        content_to_update.author = form.author.data
        content_to_update.header = form.header.data
        content_to_update.desc = form.desc.data
        content_to_update.source = form.source.data
        content_to_update.date = form.date.data
        if 'content_form_data' in session:
            content_to_update.img = session['content_form_data']['image_filename']
            content_to_update.img_credits = session['content_form_data']['image_credits']
        
        db.session.commit()
        return redirect(url_for('admin_nutrition'))