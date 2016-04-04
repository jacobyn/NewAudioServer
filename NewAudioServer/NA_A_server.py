import os

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
app.config['UPLOAD_FOLDER'] = '/var/www/NewAudioServer/NewAudioServer/uploads/'

#'/tmp/'


# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation
@app.route('/')
def index():
    return render_template('example_simple_exportwav.html')

# @app.route('/stims/<path:path>')
# def send_js(path):
#     print "trying to..."
#     print path
#     return send_from_directory('stims', path)

@app.route('/analyze', methods = ['POST'])
def anal():
    myrnd=random.randint(1000,10000)

    if request.method == 'POST':
        print request.method
        file = request.files['file']
        ofname=file.filename

        #parse fname
        pfname=ofname.split(".")
        print pfname
        assert pfname[0]=='script'
        assert pfname[2]=='file'
        mscript=secure_filename(pfname[1])
        fname=secure_filename(pfname[3])

        filename ='BBB-' + mscript + '-' + fname + '-rnd-' + str(myrnd)+ '.wav'
        #filename ='uploadedxxx.wav'
        tempfname=os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print "tempfname:" + tempfname
        #f= open('/var/www/NewAudioServer/NewAudioServer/uploads/uploaded.wav', 'rb')
        file.save(tempfname)
        print "saved in " + tempfname
        return Response(dumps({'filename': filename}), status=200, mimetype='application/json')

# def analyze():
#     myrnd=random.randint(1000,10000)
#     filename ='AAA_uploaded'+str(myrnd)+'.wav'

#     if request.method == 'POST':
#         #print request.method
#         file = request.files['file']
#         temp_fname=os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         temp_fname='stam.wav'
#         file.save(temp_fname)

#         return Response(dumps({'filename': filename}), status=200, mimetype='application/json')

# How to do send
# import requests
# url = 'http://127.0.0.1:5000/upload'
# files = {'file': open('uploads/uploaded2.wav', 'rb')}
# r = requests.post(url, files=files)
# r.text


# @app.route('/upload', methods = ['POST'])
# def upldfile():

#     if request.method == 'POST':
#         print request.method
#         file = request.files['file']
#         #filename = secure_filename(file.filename)
#         filename ='uploaded.wav'
#         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#         print "saved in " + filename
#         print file
#         return "OK"

