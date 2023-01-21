"""
Use this file to quickly run django scripts.
https://stackoverflow.com/a/39724171
"""
import django
import os
import sys


sys.path.append("atila")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "atila.settings")
django.setup()

# import statements must come AFTER django.setup() has been called

import sys
from atlas.utils_pinecone import delete_by_video_id

# todo this should be in a runscript
if len(sys.argv) < 2:
    raise Exception('a video_id argument must be supplied')

delete_by_video_id(sys.argv[1])
