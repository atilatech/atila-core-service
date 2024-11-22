"""
Use this file to quickly run django scripts.
https://stackoverflow.com/a/39724171
"""
import django
import os
import sys


sys.path.append("./atila")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "atila.settings")
django.setup()

# import statements must come AFTER django.setup() has been called

from atlas.payments import send_atlas_credits_email

send_atlas_credits_email('tomiademidun@gmail.com', "Tomiwa", 5)
