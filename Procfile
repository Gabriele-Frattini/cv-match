web: daphne admin.wsgi:appliction --port $PORT --bind 0.0.0.0 -v2
celery: celery -A admin.celery worker --pool=solo -l info
