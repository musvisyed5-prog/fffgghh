import os
import sys

# Add the 'src' directory to the python path so that Django can find 'src.settings'
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
app = application
