import os
import subprocess
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, Blueprint, Response, request, render_template
from werkzeug import secure_filename
import random
import json

import requests
import shutil
import socket
import StringIO
import urllib2

params={}

IS_MAC=True

# Initialize the Flask application
app = Flask(__name__)


# This is the path to the upload directory
if IS_MAC:
    app.config['UPLOAD_FOLDER'] = 'res/'
    app.config['RUN_FOLDER'] = 'res/' # CTUlly thiw should not be run from the mac...
#    matlab_cmd="/Applications/MATLAB_R2014b.app/bin/matlab"
else:
    app.config['UPLOAD_FOLDER'] = '/var/www/NewAudioServer/NewAudioServer/res/' ######### THIS DIRECTORY IS DIRABLE YOU NEED TO EVENTUALLY NOT ALLOW DIRRING
    app.config['RUN_FOLDER'] = '/var/www/NewAudioServer/NewAudioServer/run/' ######### THIS DIRECTORY IS
#    matlab_cmd='matlab'


##############  Heroku SERVER ###############
aver='MA2'


burl_res='http://audio.norijacoby.com/res/'


def init_params():
    LOWER_MIDI_NOTE=45
    HIGHER_MIDI_NOTE=55
    exp1_stim_list=['static/assets/melody_1.wav','static/assets/melody_2.wav','static/assets/melody_3.wav','static/assets/melody_4.wav']
    exp1={'name':'experiment 1', 'N_repetitions': 1,  'N_maxtrials':5, 'stim_list': exp1_stim_list}
    train1_stim_list=['static/assets/pitch_1.wav','static/assets/pitch_2.wav']
    train1={'name':'experiment 1', 'N_repetitions': 1,  'N_maxtrials':2, 'stim_list': train1_stim_list}
    experiments=[exp1,train1]
    params={'LOWER_MIDI_NOTE': LOWER_MIDI_NOTE, 'HIGHER_MIDI_NOTE':HIGHER_MIDI_NOTE, 'experiments': experiments}
    return params

def create_pitch_stim(midi):
    print "try_to_create_pitch: " + str(midi)

    params=dict()
    params.update( {'midi': midi, 'duration':2})
    done_ext='ogg'
    wfile=None

    url='http://audio.norijacoby.com/analyze'
    mscript='pitch_stim_create'
    session_id=str(random.randint(1000,10000))
    file_id=str(random.randint(1000,10000))

    return_route='http://audio.norijacoby.com/boo' #the url should have the following form http:/xxx/boo/is_sucess/done-fname
    sver=aver


    params.update({'url':url, 'mscript':mscript, 'session_id':session_id, 'file_id': file_id, 'return_route': return_route,'ver':sver, 'done_ext':'ogg' })
    print params
    return do_analyze(wfile,params)


def send_analyze(wfile):
    params=dict()
    done_ext='html'

    url='http://audio.norijacoby.com/analyze'
    mscript='detect_pitch_in_file_web'
    session_id=str(random.randint(1000,10000))
    file_id=str(random.randint(1000,10000))
    return_route='http://audio.norijacoby.com/set_analysis_response' #the url should have the following form http:/xxx/boo/is_sucess/done-fname
    sver=aver

    params.update({'url':url,'mscript':mscript, 'session_id':session_id, 'file_id': file_id, 'return_route': return_route,'ver':sver, 'done_ext':done_ext})

    return do_analyze(wfile,params)


def do_analyze(wfile, params):

    print "reading params..."
    sver=params['ver']
    session_id=params['session_id']
    file_id=params['file_id']
    print "HERE3"
    done_ext=params['done_ext']
    url=params['url']


    print "setting params..."
    rfilename =  sver + '.session.' + str(session_id) + '.file.' + str(file_id) +  '.rec'  + '.wav'
    pfilename = sver + '.session.' + str(session_id) + '.file.' + str(file_id)  + '.todo' + '.json'
    mlogfilename =  sver + '.session.' + str(session_id) + '.file.' + str(file_id)  + '.mlog' + '.txt'
    donefilename =  sver + '.session.' + str(session_id) + '.file.' + str(file_id)  + '.done.' + done_ext


    params['rfilename']=rfilename
    params['pfilename']=pfilename
    #params['matlab_cmd']=matlab_cmd
    params['mlogfilename']=mlogfilename
    params['donefilename']=donefilename

    #print matlab_cmd

    #params['mlogfilename']=pfilename

    print "preparing files..."

    pfile = StringIO.StringIO(json.dumps(params))
    if wfile is None:
        wfile = StringIO.StringIO("<empty>")

    # if fileNone is None:
    #     files = {'rec': (rfilename, file), 'param': (pfilename,pfile)}
    # else:
    #     files = {'rec': (rfilename, file), 'param': (pfilename,pfile)}

    files = {'rec': (rfilename, wfile), 'param': (pfilename,pfile)}

    print('trying to send...')
    r = requests.post(url, files=files)
    pfile.close()
    print('OK response... :' + r.text)
    return r.text




@app.route('/')
def run_pitch():
    return render_template('MelodyGame02.html')



@app.route('/getAudioFileName', methods = ['GET'])
def getAudioFileName_route():
    #print("here...")
    filename='http://audio.norijacoby.com/stims/stim1.ogg'
    print ("got a get request returning filename: " + filename)
    out= json.dumps({"fname": filename})
    print out
    return Response(out, status=200, mimetype='application/json')


@app.route('/upload', methods = ['POST'])
def upload_route():
    try:
        if request.method == 'POST':
            wfile = request.files['file']
            print "about to  sent: "
            return send_analyze(wfile)
    except Exception as e:
        print(e)

@app.route("/createpitch/<int:midi>", methods = ['GET'])
def createpitch_route(midi):
    try:
        data=create_pitch_stim(midi)
    except Exception as e:
        print(e)
    return Response(data, status=200, mimetype='application/json')


@app.route("/get_results_file/<rfile>", methods = ['GET'])
def get_results_file_route(rfile):
    murl=burl_res+rfile
    print "trying to get result file: " + murl
    try:

        data = requests.get(murl)
        print "read_data"
        print data
    except Exception as e:
        print(e)
    return Response(data.text, status=200, mimetype='application/html')





##############  MATLAB SERVER ###############


def shellquote(s):
    return "'" + s.replace("'", "'\\''") + "'"


# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation

@app.route('/test')
def test():
    mver='107'
    print "*******************"
    print "testing, ver: " + mver
    print "*******************"
    return mver


@app.route('/clear')
def clear_res_dir():
    cmd='cd /var/www/NewAudioServer/NewAudioServer/res/;rm M*.wav; rm M*.txt; rm M*.mat; rm M*.json; rm M*.ogg'
    os.system(cmd)
    cmd='cd /var/www/NewAudioServer/NewAudioServer/run/;rm M*.sh'
    os.system(cmd)
    return "CLEARED!"


@app.route('/boo2')
def boo2():
    return "boo2!"

@app.route("/boo/<int:is_sucess>/<pfile>", methods=["GET"])
def boo(is_sucess,pfile):
    data = {"aaa":"boo", "status": "success", "is_sucess": int(is_sucess), "pfile": pfile}
    return Response(json.dumps(data), status=200, mimetype='application/json')

@app.route("/set_analysis_response/<int:is_sucess>/<pfile>", methods=["GET"])
def set_analysis_response2(is_sucess,pfile):
    data = {"aaa":"anal", "status": "success", "is_sucess": int(is_sucess), "pfile": pfile}
    return Response(json.dumps(data), status=200, mimetype='application/json')


@app.route('/get_params/<participant_id>', methods = ['GET'])
def get_params(participant_id):
    params=init_params()
    print params
    try:
          return Response(json.dumps(params), status=200, mimetype='application/json')

    except Exception as e:
        print(e)
        return Response(str(e), status=400, mimetype='application/json')


@app.route('/analyze', methods = ['POST'])
def anal():

    try:
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
            mlogfilename=os.path.join(app.config['UPLOAD_FOLDER'], mlogfilename)

            pfilename=params['pfilename']
            matlab_cmd= '/usr/local/bin/matlab -nodisplay -nodesktop -nosplash -nojvm -r "MA_Mwraper(\'' + pfilename +  "\'); exit\" > " + mlogfilename
            #matlab_cmd= matlab_cmd.replace('XXXXXX/',app.config['UPLOAD_FOLDER'])
            #matlab_cmd=os.path.join(app.config['UPLOAD_FOLDER'], matlab_cmd)


            # create a script shell and run it
            #######################################
            session_id=params['session_id']
            file_id=params['file_id']
            sver=params['ver']
            mscript=params['mscript']

            rfname =  sver + '.session.' + str(session_id) + '.file.' + str(file_id) +  '.run.sh'
            rfname=os.path.join(app.config['RUN_FOLDER'],rfname)

            print "rfname:{}".format(rfname)

            with open(rfname, "w") as text_file:
                 text_file.write("#!/bin/bash\n \n cd /var/www/NewAudioServer/NewAudioServer\n\n " + matlab_cmd)
            chmod_fname='chmod u+x ' +rfname

            print "cfname:{}".format(chmod_fname)

            os.system(chmod_fname)

            print "matlab_cmd= {}".format(matlab_cmd)

            os.system("sudo su - root " + rfname + " & ")
            ##########################################  end of script shell creating
            print "*************************************************"
            print "*** seems to be ok:\n *** running= {}\n *** rfname={} \n *** script={} ".format(matlab_cmd,rfname,mscript)
            print "**************************************************"

            return Response(json.dumps(params), status=200, mimetype='application/json')

    except Exception as e:
        print(e)
        return Response(str(e), status=400, mimetype='application/json')


if __name__ == '__main__':
   app.run()

