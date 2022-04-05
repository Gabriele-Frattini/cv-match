import os 
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin.settings')

app = Celery('admin')

app = Celery('tasks', backend='rpc://', broker='pyamqp://')

app.autodiscover_tasks()

