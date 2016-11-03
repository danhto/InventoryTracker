"""
WSGI config for InventoryTracker project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application
from django.contrib.auth.handlers.modwsgi import check_password
from django.core.handlers.wsgi import WSGIHandler

sys.path.append('/Users/clubs/Desktop/IT/Python/InventoryTracker/')
sys.path.append('/Users/clubs/Desktop/IT/Python/InventoryTracker/InventoryTracker/wsgi.py')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "InventoryTracker.settings")

"""
application = WSGIHandler()
"""
application = get_wsgi_application()
