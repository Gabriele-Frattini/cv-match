release: python manage.py migrate
web: daphne admin.wsgi:appliction --port $PORT --bind 0.0.0.0 -v2
celery: celery -A admin.celery worker -l info
