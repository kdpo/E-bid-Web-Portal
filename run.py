#!venv/bin/python 
'''
from app import app
app.run(debug=True, host='0.0.0.0') 
'''
from flask import Flask
from app.views import site

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379'

app.register_blueprint(site)

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')
