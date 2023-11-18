# importing libraries 
from flask import Flask 
from flask_mail import Mail, Message 

app = Flask(__name__) 
mail = Mail(app) # instantiate the mail class 

# configuration of mail 
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 3000
app.config['MAIL_USERNAME'] = 'slacktestingeventcat'
app.config['MAIL_PASSWORD'] = 'a1234567!'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app) 

# message object mapped to a particular URL ‘/’ 

msg = Message( 
                    'Hello', 
                    sender ='slacktestingeventcat@gmail.com', 
                    recipients = ['dae@xl8.ai'] 
                ) 
msg.body = 'Hello Flask message sent from Flask-Mail'
mail.send(msg) 

if __name__ == '__main__': 
    app.run(debug = True) 