import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'url_shortener.settings')
app = Celery('url_shortener')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()