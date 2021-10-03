import json
import requests
from flask_babel import _
from app import app

# I did not sign up for a translation service so I'm just going to 
# process the text in some way and return it to learn the AJAX functionality
def translate(text, source_language, dest_language):
    newText = '?[' + text + ']?'
    return newText