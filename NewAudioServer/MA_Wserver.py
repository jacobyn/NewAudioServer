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
import socket
import StringIO

aver='MA1'

# Initialize the Flask application
app = Flask(__name__)

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'

url='http://audio.norijacoby.com/analyze'

def send_analyze(file):
     mscript='AudioInfo'
     session_id=str(random.randint(1000,10000))
     file_id=random.randint(1000,10000)
     return_route='AnalyzeReady'

     params={'mscript':mscript, 'session_id':session_id, 'file_id': file_id, 'return_route': return_route,'ver':aver }


     return send_do(file, params)

def send_do(file, params):
    session_id=params['session_id']
    file_id=params['file_id']
    sver=params['ver']
    rfilename =  sver + '.session.' + str(session_id) + '.file.' + str(file_id) +  '.rec'  + '.wav'
    pfilename = sver + '.session.' + str(session_id) + '.file.' + str(file_id)  + '.todo' + '.json'
    mlogfilename = "res/" + sver + '.session.' + str(session_id) + '.file.' + str(file_id)  + '.mlog' + '.txt'

    matlab_cmd= 'matlab -nodisplay -nodesktop -nosplash -nojvm -r "MA_Mwraper(\'' + pfilename +  "\'); exit\" > " + mlogfilename

    params['rfilename']=rfilename
    params['pfilename']=pfilename
    params['matlab_cmd']=matlab_cmd
    print matlab_cmd

    #params['mlogfilename']=pfilename


    pfile = StringIO.StringIO(dumps(params))

    files = {'rec': (rfilename, file), 'param': (pfilename,pfile)}
    r = requests.post(url, files=files)
    pfile.close()
    print r.text
    return "OK: " + r.text

# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation
@app.route('/')
def index():
    return render_template('NA_client.html')

# @app.route('/getdom')
# def get_domain():
#     domain = socket.gethostname()
#     print "**********"
#     print domain
#     print "***********"
#     return domain

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
