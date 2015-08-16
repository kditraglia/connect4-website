import os, sys
import django.core.handlers.wsgi


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../game/")))

os.environ['DJANGO_SETTINGS_MODULE'] = 'connect4.settings'
application = django.core.handlers.wsgi.WSGIHandler()

