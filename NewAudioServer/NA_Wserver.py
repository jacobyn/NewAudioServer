import os
# We'll render HTML templates and access data sent by POST
# using the request object from flask. Redirect and url_for
# will be used to redirect the user once the upload is done
# and send_from_directory will help us to send/show on the
# browser the file that the user just uploaded
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, Blueprint, Response, request, render_template
from werkzeug import secure_filename
import random
from json import dumps
import os
import requests
import shutil

# Initialize the Flask application
app = Flask(__name__)

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'

def send_analyze(file):
     mscript='AudioInfo'
     url='http://audio.norijacoby.com/analyze'
     session_id=str(random.randint(1000,10000))
     myrnd=random.randint(1000,10000)
     tfname='fileToUpload' +str(myrnd)
     return_route='AnalyzeReady'
     return send_do(file, session_id, mscript,  tfname, return_route)

def send_do(file, session_id='9999', script='AudioInfo', fname_orig='temp', return_route='AnalyzeReady'):
    filename ='session.' + session_id + '.script.' + script + '.file.' + fname_orig + '.rroute.' + return_route + '.wav'
    files = {'file': (filename, file)}
    r = requests.post(url, files=files)
    print r.text
    return "OK"

# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation
@app.route('/')
def index():
    return render_template('NA_client.html')

@app.route('/getAudioFileName', methods = ['GET'])
def getAudioFileName():
    #print("here...")
    filename='http://audio.norijacoby.com/stims/stim1.ogg'
    print ("got a get request returning filename: " + filename)
    out= dumps({"fname": filename})
    print out
    return Response(out, status=200, mimetype='application/json')


@app.route('/upload', methods = ['POST'])
def upldfile():
    try:
        if request.method == 'POST':
            file = request.files['file']
            print "about to  sent: "
            return send_analyze(file)
    except Exception as e:
        print(e)

if __name__ == '__main__':
   app.run()

# @app.route('/upload', methods = ['POST'])
# def upldfile():
#     try:
#         if request.method == 'POST':
#             file = request.files['file']
#             print "about to  sent: "
#             return send_analyze(file)
#     except Exception as e:
#         print(e)




# How to do send
# import requests
# url = 'http://127.0.0.1:5000/upload'
# files = {'file': open('uploads/uploaded2.wav', 'rb')}
# r = requests.post(url, files=files)
# r.text
