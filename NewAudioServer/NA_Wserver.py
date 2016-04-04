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
        mscript='analyze.m'
        url='http://audio.norijacoby.com/analyze'
        myrnd=random.randint(1000,10000)
        filename ='uploaded'+str(myrnd)+'.wav'

        print "analyzing response... of upload post"
        if request.method == 'POST':
            print request.method
            file = request.files['file']
            temp_fname=os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(temp_fname)
            print "about to  sent: " + temp_fname
            files = {'file': open(temp_fname, 'rb')}
            r = requests.post(url, files=files)
            print "was sent"
            print r.text
            return "OK"
    except Exception as e:
        print(e)


if __name__ == '__main__':
   app.run()

# How to do send
# import requests
# url = 'http://127.0.0.1:5000/upload'
# files = {'file': open('uploads/uploaded2.wav', 'rb')}
# r = requests.post(url, files=files)
# r.text
