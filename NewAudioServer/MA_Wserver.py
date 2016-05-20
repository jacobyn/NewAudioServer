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

IS_MAC=False


aver='MA1'

# Initialize the Flask application
app = Flask(__name__)



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
    done_ext='txt'

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

    pfile = StringIO.StringIO(dumps(params))
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




# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation
# @app.route('/')
# def index():
#     return render_template('NA_client.html')

@app.route('/')
def index():
    return render_template('MA_pitchgame.html')


# @app.route('/getdom')
# def get_domain():
#     domain = socket.gethostname()
#     print "**********"
#     print domain
#     print "***********"
#     return domain

@app.route('/getAudioFileName', methods = ['GET'])
def getAudioFileName_route():
    #print("here...")
    filename='http://audio.norijacoby.com/stims/stim1.ogg'
    print ("got a get request returning filename: " + filename)
    out= dumps({"fname": filename})
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
