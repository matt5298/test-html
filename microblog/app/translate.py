import json
import requests
from flask import current_app
from flask_babel import _

# I did not sign up for a translation service so I'm just going to 
# process the text in some way and return it to learn the AJAX functionality
def translate(text, source_language, dest_language):
    newText = source_language + "=>"+ dest_language +' ?['+ text + ']?'
    return newText