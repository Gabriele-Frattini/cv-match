"""
ASGI config for resumeMatcher project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""
# from django.core.asgi import get_asgi_application


import os
import django
from channels.routing import get_default_appliction


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin.settings')
django.setup()
application = get_default_appliction()
