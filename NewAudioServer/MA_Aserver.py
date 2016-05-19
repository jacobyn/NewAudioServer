import os
import subprocess
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, Blueprint, Response, request, render_template
from werkzeug import secure_filename
import random
import json
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
    app.config['UPLOAD_FOLDER'] = '/var/www/NewAudioServer/NewAudioServer/res/' ######### THIS DIRECTORY IS DIRABLE YOU NEED TO EVENTUALLY NOT ALLOW DIRRING
    app.config['RUN_FOLDER'] = '/var/www/NewAudioServer/NewAudioServer/run/' ######### THIS DIRECTORY IS
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
    mver='106'
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

#         return Response(json.dumps({'filename': filename, 'cmd': cmd}), status=200, mimetype='application/json')

@app.route('/clear')
def clear_res_dir():
    cmd='cd /var/www/NewAudioServer/NewAudioServer/res/;rm M*.wav; rm M*.txt; rm M*.mat; rm M*.json'
    os.system(cmd)
    return "CLEARED!"


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

        rfname=os.path.join(app.config['UPLOAD_FOLDER'], orfname)
        print "rfname:" + rfname
        rfile.save(rfname)
        print "saved in: " + rfname

        pfname=os.path.join(app.config['UPLOAD_FOLDER'], opfname)

        resdir=app.config['UPLOAD_FOLDER']

        print "pfname:" + pfname
        pfile.save(pfname)
        print "saved in: " + pfname

        print 'read paramters...'
        pf=open(pfname,'r')
        params=json.load(pf)
        print params


        mlogfilename=params['mlogfilename']
        pfilename=params['pfilename']
        matlab_cmd= '/usr/local/bin/matlab -nodisplay -nodesktop -nosplash -nojvm -r "MA_Mwraper(\'' + pfilename +  "\'); exit\" > " + mlogfilename
        matlab_cmd= matlab_cmd.replace('XXXXXX/',app.config['UPLOAD_FOLDER'])

#        matlab_cmd= matlab_cmd.replace('XXXXXX/',app.config['UPLOAD_FOLDER'])

        #matlab_cmd= matlab_cmd.replace('XXXXXX/',app.config['UPLOAD_FOLDER'])

        #matlab_cmd=os.path.join(app.config['UPLOAD_FOLDER'], matlab_cmd)


        # create a script shell and run it
        #######################################
        session_id=params['session_id']
        file_id=params['file_id']
        sver=params['ver']

        rfname =  sver + '.session.' + str(session_id) + '.file.' + str(file_id) +  '.run.sh'
        rfname=os.path.join(app.config['RUN_FOLDER'],rfname)

        print "rfname:{}".format(rfname)

        with open(rfname, "w") as text_file:
             text_file.write("#!/bin/bash\n cd /var/www/NewAudioServer/NewAudioServer\n" + matlab_cmd)
        chmod_fname='chmod u+x ' +rfname

        print "cfname:{}".format(chmod_fname)

        os.system(chmod_fname)

        print "matlab_cmd= {}".format(matlab_cmd)

        os.system("sudo su - root " + rfname + " & ")
        ##########################################  end of script shell creating
        print "*************************************************"
        print "*** seems to be ok:\n *** running= {}\n *** rfname={} ".format(matlab_cmd,rfname)
        print "**************************************************"

        return Response(json.dumps({'pfname': opfname}), status=200, mimetype='application/json')


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

        # return Response(json.dumps({'filename': filename, 'cmd': cmd}), status=200, mimetype='application/json')

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

#         return Response(json.dumps({'filename': filename}), status=200, mimetype='application/json')

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

