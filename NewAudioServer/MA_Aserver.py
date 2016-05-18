import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, Blueprint, Response, request, render_template
from werkzeug import secure_filename
import random
from json import dumps
import os
import requests
import shutil

IS_MAC=False

# Initialize the Flask application
app = Flask(__name__)

# This is the path to the upload directory
if IS_MAC:
    app.config['UPLOAD_FOLDER'] = 'res/'
    matlab_cmd="/Applications/MATLAB_R2014b.app/bin/matlab"
else:
    app.config['UPLOAD_FOLDER'] = '/var/www/NewAudioServer/NewAudioServer/res/'
    matlab_cmd='matlab'

#'/tmp/'

def shellquote(s):
    return "'" + s.replace("'", "'\\''") + "'"


# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation
@app.route('/')
def index():
    return render_template('example_simple_exportwav.html')

@app.route('/test')
def test():
    mver='102'
    print "*******************"
    print "testing, ver: " + mver
    print "*******************"
    return mver

# @app.route('/stims/<path:path>')
# def send_js(path):
#     print "trying to..."
#     print path
#     return send_from_directory('stims', path)

# @app.route('/do', methods = ['POST'])
# def do():
#     myrnd=random.randint(1000,10000)

#     print "trying to process POST rq."
#     if request.method == 'POST':
#         print request.method
#         file = request.files['file']
#         pfname=file.filename.split(".")
#         print pfname
#         #filename ='session.' + session_id + '.script.' + script + '.file.' + fname_orig + '.rroute.' + return_route + '.wav'

#         assert pfname[0]=='session_id'
#         assert pfname[2]=='script'
#         assert pfname[4]=='file'
#         assert pfname[6]=='rroute'
#         session_id= pfname[1]
#         script= pfname[3]
#         fname_orig= pfname[5]
#         return_route= pfname[7]

#         filename ='RES-' + session_id + '-' + script + '-' + fname_orig + '-' + return_route + '-rnd-' + str(myrnd)+ '.wav'

#         tfname=os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         print "tfname:" + tfname

#         file.save(tempfname)
#         print "saved in " + tempfname

#         cmd = matlab_cmd + " -nodisplay -nodesktop -nosplash -nojvm -r \" wraper (\'" + tfname + "\', \'" + script + "\', \'" + rroute + "\' ); exit\" >" + filename + ".log &"
#         print cmd
#         os.system(cmd)

#         return Response(dumps({'filename': filename, 'cmd': cmd}), status=200, mimetype='application/json')


@app.route('/analyze', methods = ['POST'])
def anal():
    myrnd=random.randint(1000,10000)

    print "trying to process POST rq."
    if request.method == 'POST':
        print request.method
        rfile = request.files['rec']
        pfile = request.files['param']
        opfname=pfile.filename
        orfname=rfile.filename

        pfname=os.path.join(app.config['UPLOAD_FOLDER'], opfname)
        print "pfname:" + pfname
        pfile.save(pfname)
        print "saved in: " + pfname

        rfname=os.path.join(app.config['UPLOAD_FOLDER'], orfname)
        print "rfname:" + rfname
        rfile.save(rfname)
        print "saved in: " + rfname
        return Response(dumps({'pfname': opfname}), status=200, mimetype='application/json')


        # #f= open('/var/www/NewAudioServer/NewAudioServer/uploads/uploaded.wav', 'rb')
        # file.save(tempfname)
        # print "saved in " + tempfname

        # #parse fname
        # pfname=ofname.split(".")
        # print pfname
        # assert pfname[0]=='session'
        # assert pfname[2]=='script'
        # assert pfname[4]=='file'
        # session_id=secure_filename(pfname[1])
        # mscript=secure_filename(pfname[3])
        # fname=secure_filename(pfname[5])

        # filename ='BBB-' + session_id + '-' + mscript + '-' + fname + '-rnd-' + str(myrnd)+ '.wav'
        # #filename ='uploadedxxx.wav'
        # tempfname=os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # print "tempfname:" + tempfname
        # #f= open('/var/www/NewAudioServer/NewAudioServer/uploads/uploaded.wav', 'rb')
        # file.save(tempfname)
        # print "saved in " + tempfname

        # cmd = matlab_cmd + " -nodisplay -nodesktop -nosplash -nojvm -r \"AudioInfo(\'" + tempfname + "\'); exit\" > temp.out &"
        # print cmd
        # os.system(cmd)

        # return Response(dumps({'filename': filename, 'cmd': cmd}), status=200, mimetype='application/json')

if __name__ == '__main__':
   app.run()
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

