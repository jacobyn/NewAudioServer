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


# Initialize the Flask application
app = Flask(__name__)

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'

# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation
@app.route('/')
def index():
    return render_template('NA_client.html')

@app.route('/getAudioFileName', methods = ['GET'])
def getAudioFileName():
    print("here...")
    filename='audio.norijacoby.com/stims/stim1.ogg'
    print ("got a get request returning filename: " + filename)
    out= dumps({"fname": filename})
    print out
    return Response(out, status=200, mimetype='application/json')


@app.route('/upload', methods = ['POST'])
def upldfile():

    if request.method == 'POST':
        print request.method
        file = request.files['file']
        #filename = secure_filename(file.filename)
        filename ='uploaded.wav'
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print "saved in " + filename
        print file
        return "OK"


if __name__ == '__main__':
   app.run()

# How to do send
# import requests
# url = 'http://127.0.0.1:5000/upload'
# files = {'file': open('uploads/uploaded2.wav', 'rb')}
# r = requests.post(url, files=files)
# r.text
