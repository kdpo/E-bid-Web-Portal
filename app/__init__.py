from flask import Flask 
from flask_mail import Mail
from shareplum import Site, Office365
from shareplum.site import Version

app = Flask(__name__)
app.config.from_object('config') 
mail = Mail(app) 

from app import views
