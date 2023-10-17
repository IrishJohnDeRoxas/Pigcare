from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import smtplib, datetime, time

sender = 'pigcarethesis@gmail.com'
password = 'vnku mpel fxzo wmxc'
receiver = 'yoteyob718@estudys.com'

# Create a message object
msg1 = MIMEMultipart()

# Set the sender and recipient
msg1['From'] = sender
msg1['To'] = receiver

# Set the subject
msg1['Subject'] = 'Reminder: Due Date'

# # Add an image to the email
# with open('image.jpg', 'rb') as f:
#     img_data = f.read()
# img = MIMEImage(img_data)
# msg1.attach(img)

# Get the current date and time for the mean time
datetime_from_user = datetime.datetime.now()

# Calculate the 2 weeks and 2 days from now
two_weeks_before_due_date = datetime_from_user + datetime.timedelta(seconds=20) # 20secs for now
two_days_before_due_date = datetime_from_user + datetime.timedelta(seconds=10)

# Calculate the number of seconds between now and the future time
first_reminder = (two_weeks_before_due_date - datetime_from_user).total_seconds()
second_reminder = (two_days_before_due_date - datetime_from_user).total_seconds()



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
        PigcCare thesis reminder - {two_weeks_before_due_date.strftime('%a, %d %b %Y - %H:%M:%S')}
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
   
   #------------------------------------------------------------------------------------ 
# Set the sender and recipient
msg2 = MIMEMultipart()

msg2['From'] = sender
msg2['To'] = receiver

# Set the subject
msg2['Subject'] = 'Reminder: Due Date'

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