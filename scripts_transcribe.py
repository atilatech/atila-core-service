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

from atlas.transcribe_collection import calculate_cost_for_transcribing_a_collection
# url = "https://www.youtube.com/watch?v=aUlLLnsvwKE"  # 24 Hours With Emma Chamberlain in Copenhagen | Vogue
url = "https://www.youtube.com/watch?v=WNvOtwP_yf4"  # Making Friends with Machine Learning: Regression
# Sam Parr: From Jail To $20+ Million By 32 | The Danny Miranda Podcast 243
# url = "https://www.youtube.com/watch?v=xKSIOI-wpSQ"
# INSANE GAME! Los Angeles Lakers vs Dallas Mavericks Final Minutes ! 2022-23 NBA Season
# url = "https://www.youtube.com/watch?v=31DsvAWXryY"
# A visual guide to Bayesian thinking
# url = "https://www.youtube.com/watch?v=BrK7X_XlGB8"

# print("get_transcript_from_youtube(url)", get_transcript_from_youtube(url))

if __name__ == "__main__":
    playlist_url = 'https://www.youtube.com/playlist?list=PLS1QulWo1RIaJECMeUT4LFwJ-ghgoSH6n'
    channel_url = 'https://www.youtube.com/c/ProgrammingKnowledge'
    channel_url = 'https://www.youtube.com/channel/UCG2iWiYgJYkjBl4EdYGI5mw'
    print("get_transcript_from_youtube(url)", calculate_cost_for_transcribing_a_collection(channel_url))
