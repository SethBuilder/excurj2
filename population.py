import os
from os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tango_with_django_proj.settings')

import django
django.setup()

from excurj.models import City