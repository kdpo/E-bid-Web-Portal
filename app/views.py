from flask import Blueprint, render_template, request, jsonify, make_response
from .validators import isExistingFolder, isValidEmail
import time
import os
from decouple import config
import base64
from celery import Celery 

site = Blueprint('site', __name__, template_folder='templates', static_folder='static', static_url_path='/static/style.css')

celery = Celery('tasks',  
                broker= config('REDIS_DATABASE'),
                backend= config('REDIS_DATABASE'))

@site.route('/api/get_public_key/') 
def api_get_public_key(): 
    data = ''
    with open(config('PUBLIC_KEY'), 'r') as file:
        data = file.read()
    public_key = data

    return jsonify({ 
        'public_key': public_key 
    }) 

@site.route('/')
def root(): 
    return render_template('index_v2.html')

@site.route('/decrypt')
def decryption():
    return render_template('decrypt.html')

@site.route('/process', methods=['GET', 'POST'])
def process():
    if request.method == "POST":
        
        email = request.form.get('email')
        bid_id =  request.form.get('bid_id')
        formFile = request.files['formFile']

        if email and bid_id:
            if not isValidEmail(email):
                return make_response(jsonify({'error' : 'Please enter a valid email address.'}), 400)

            fileObject = formFile.read()            
            
            try:
                if isExistingFolder(bid_id):
                    base64_bytes = base64.b64encode(fileObject)
                    base64_message = base64_bytes.decode('ascii')

                    # save to Sharepoint
                    if config('ALLOW_SHAREPOINT') == 'True':
                        celery.send_task('celery_tasks.sharepoint_upload', args=[str(bid_id), base64_message, formFile.filename])
                    date_time = time.strftime("%b %d %Y %I:%M %p")
                    # send email
                    if config('ALLOW_GMAIL') == 'True':
                        celery.send_task('celery_tasks.send_email', args=[email, base64_message, formFile.filename, date_time])
                    # save to minio
                    if config('ALLOW_MINIO') == 'True':
                        celery.send_task('celery_tasks.minio_upload', args=[bid_id, base64_message, formFile.filename])
                    # save to local file system
                    celery.send_task('celery_tasks.file_system_upload', args=[bid_id, base64_message, formFile.filename])
                    return jsonify({'filename' : formFile.filename, 'time': date_time})
                    
                else:
                    return make_response(jsonify({'error' : 'Bid ID '+ bid_id +' does not exist!'}), 404)
           
            except Exception as e:
                print(e)
                return make_response(jsonify({'error' : 'Connection timed out. Try again later.'}), 500)                   
    return make_response(jsonify({'error' : 'Please fill out all fields.'}), 400)
