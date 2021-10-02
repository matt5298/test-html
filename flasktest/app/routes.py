from app import app
import sys
from flask import request

varDebug = True

def debugURL():
    #troubleshooting url problems
    print("debug: " + request.root_url)
    print("debug: " + request.url)


@app.route('/')
@app.route('/index')
def index():
    if varDebug:
        debugURL()
    #print ('In route /', file=sys.stderr)
    #print (request.root_url)
    return "Hello Matt's world!!!!"

@app.route('/<path:u_path>')
def catch_all(u_path):
    if varDebug:
        debugURL()
    print(repr(u_path))
    return repr(u_path)
