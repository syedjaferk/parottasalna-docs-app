"""Run from this folder:  python app.py"""
import settings
import settings as same_settings      # a second import gets the cached module

settings.DEBUG = True
print(same_settings.DEBUG)            # True: everyone importing settings sees the change
print(settings is same_settings)      # True
