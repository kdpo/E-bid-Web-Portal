from celery import Celery
import base64
from shareplum import Site, Office365
from shareplum.site import Version
from app.emails import send
import os
from decouple import config
import redis
from minio import Minio
from minio.error import ResponseError
from io import BytesIO

minioClient = Minio(config('MINIO_HOST'), access_key=config('MINIO_ACCESS_KEY'), secret_key=config('MINIO_SECRET_KEY'), secure=False)

celery = Celery('tasks',  
                broker= config('REDIS_DATABASE'),
                backend= config('REDIS_DATABASE'))


@celery.task(name='celery_tasks.send_email')
def send_async_mail(receiver, base64_message, filename, date_time):
	base64_bytes = base64_message.encode('ascii')
	message_bytes = base64.b64decode(base64_bytes)
	send(receiver, message_bytes, filename, date_time)
	return "success"

@celery.task(name='celery_tasks.sharepoint_upload')
def sharepoint_upload(bid_id, base64_message, filename):
	authcookie = Office365(config('SHAREPOINT_SITE'), username=config('SHAREPOINT_USERNAME'), password=config('SHAREPOINT_PASSWORD')).GetCookies()
	site = Site(config('SHAREPOINT_FOLDER_LOCATION'), version=Version.v2016, authcookie=authcookie)
	folder = site.Folder(config('SHAREPOINT_FOLDERNAME') +'/%s' % bid_id)
	
	base64_bytes = base64_message.encode('ascii')
	message_bytes = base64.b64decode(base64_bytes)

	folder.upload_file(message_bytes, filename)
	return "success"

@celery.task(name='celery_tasks.file_system_upload')
def file_upload(bid_id, base64_message, filename):
	base64_bytes = base64_message.encode('ascii')
	message_bytes = base64.b64decode(base64_bytes)

	with open(os.path.join(config('UPLOAD_PATH'), "{0}/{1}".format(bid_id, filename)), "wb") as fp:
		fp.write(message_bytes)

	return "success"

@celery.task(name='celery_tasks.minio_upload')
def minio_upload(bid_id, base64_message, filename):
	base64_bytes = base64_message.encode('ascii')
	message_bytes = base64.b64decode(base64_bytes)
	content = BytesIO(message_bytes)
	
	size = content.getbuffer().nbytes
	objectName = bid_id + "/" + filename;
	
	minioClient.put_object('bids', objectName, content, size)
	return "success"

