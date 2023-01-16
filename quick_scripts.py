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
from atlas.transcribe import get_transcript_from_youtube

url = "https://www.youtube.com/watch?v=aUlLLnsvwKE"  # 24 Hours With Emma Chamberlain in Copenhagen | Vogue
# Sam Parr: From Jail To $20+ Million By 32 | The Danny Miranda Podcast 243
# url = "https://www.youtube.com/watch?v=xKSIOI-wpSQ"
# INSANE GAME! Los Angeles Lakers vs Dallas Mavericks Final Minutes ! 2022-23 NBA Season
# url = "https://www.youtube.com/watch?v=31DsvAWXryY"

# print("get_manual_transcript(url)", get_manual_transcript(url))

print("get_manual_transcript(url)", get_transcript_from_youtube(url))
