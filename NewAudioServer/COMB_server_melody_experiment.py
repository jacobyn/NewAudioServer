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
from os import listdir
from os.path import isfile, join



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
burl='http://audio.norijacoby.com'
burl_audio='http://audio.norijacoby.com'

def get_urls_num_notes(mypath, repetitions=1):
    files_original = [f for f in listdir(mypath) if (isfile(join(mypath, f)) and f.split(".")[-1]=='wav') ]
    files=[]
    for i in range(repetitions):
        files=files+files_original
    number_of_notes=[f.split("n.")[1].split(".")[0] for f in files]
    murls=["{}/{}/{}".format(burl,mypath,f) for f in files]
    return (murls,number_of_notes)


    #print murls
    #print number_of_notes

    return (murls,number_of_notes)

def init_params(is_female=True):

    descr1="1. You will hear a tone.<br>2. Right after the tone, sing the same tone as accurately as possible. <br> 3. Please use the syllable 'la' for singing"
    descr2="1. You will hear a short melody.<br> 2. Immediately after the end of the melody, sing the note you think comes next. <br> 3. Please use the syllable 'la' for singing"
    trial_messages1=['Sing the same tone as accurately as possible!','Thank you!']
    trial_messages2=['Sing the note you think comes next!','Thank you!']


    # exp1_stim_list=['http://audio.norijacoby.com/stims/HC49am.wav','http://audio.norijacoby.com/stims/HC50am.wav','http://audio.norijacoby.com/stims/HC51am.wav'];
    # exp1_num_notes=[9,9,9];
    if is_female:
        (exp1_stim_list,exp1_num_notes)=get_urls_num_notes('stims/pitches_female',2)
        (exp2_stim_list,exp2_num_notes)=get_urls_num_notes('stims/melodies_female',1)
    else:
        (exp1_stim_list,exp1_num_notes)=get_urls_num_notes('stims/pitches_male',2)
        (exp2_stim_list,exp2_num_notes)=get_urls_num_notes('stims/melodies_male',1)

    max_trials_1=3
    max_trials_2=3

    max_trials_1=len(exp1_num_notes)
    max_trials_2=len(exp2_num_notes)

    exp1={'name':'Game 1: Pitch matching', 'description': descr1, 'trial_messages':trial_messages1, 'N_repetitions': 1,  'N_maxtrials':max_trials_1, 'stim_list':exp1_stim_list,'num_notes':exp1_num_notes}

    exp2={'name':'Game 2: Continue the melody','description':descr2, 'trial_messages':trial_messages2, 'N_repetitions': 1,  'N_maxtrials':max_trials_2, 'stim_list':exp2_stim_list, 'num_notes':exp2_num_notes}
    # print "numnotes 1"
    # print exp1_num_notes
    # print "numnotes 2"
    # print exp2_num_notes

    experiments=[exp1, exp2]
    params={'experiments': experiments}
    ## use title name < you allready have it>
    ## use instrcution
    return params

def init_params_const(is_female=True):

    experiments_female=[{'name': 'Game 1: Pitch matching', 'trial_messages': ['Sing the same tone as accurately as possible!', 'Thank you!'], 'N_repetitions': 1, 'stim_list': ['http://audio.norijacoby.com/stims/pitches_female/female.55.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.56.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.57.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.58.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.59.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.60.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.61.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.62.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.63.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.64.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.65.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.66.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.67.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.68.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.69.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.70.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.71.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.72.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.55.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.56.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.57.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.58.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.59.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.60.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.61.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.62.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.63.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.64.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.65.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.66.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.67.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.68.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.69.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.70.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.71.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_female/female.72.mid.n.1.wav'], 'num_notes': ['1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1'], 'N_maxtrials': 36, 'description': "1. You will hear a tone.<br>2. Right after the tone, sing the same tone as accurately as possible. <br> 3. Please use the syllable 'la' for singing"}, {'name': 'Game 2: Continue the melody', 'trial_messages': ['Sing the note you think comes next!', 'Thank you!'], 'N_repetitions': 1, 'stim_list': ['http://audio.norijacoby.com/stims/melodies_female/AC01s.female.n.6.wav', 'http://audio.norijacoby.com/stims/melodies_female/AC03s.female.n.6.wav', 'http://audio.norijacoby.com/stims/melodies_female/AC05s.female.n.7.wav', 'http://audio.norijacoby.com/stims/melodies_female/AC07s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/AC09s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/AC11s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/AC13s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/AC15s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/AC17s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/AC19s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/AC21s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/AC23s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/AC25s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/AC27s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/AC29s.female.n.8.wav', 'http://audio.norijacoby.com/stims/melodies_female/AC31s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/AC33s.female.n.8.wav', 'http://audio.norijacoby.com/stims/melodies_female/AC35s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/AC37s.female.n.8.wav', 'http://audio.norijacoby.com/stims/melodies_female/AC39s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/AC41s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/AC43s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/AC45s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/AC47s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/AC49s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/AC51s.female.n.8.wav', 'http://audio.norijacoby.com/stims/melodies_female/AC53s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/AC55s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/AC57s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/AC59s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/NC02s.female.n.8.wav', 'http://audio.norijacoby.com/stims/melodies_female/NC04s.female.n.8.wav', 'http://audio.norijacoby.com/stims/melodies_female/NC06s.female.n.8.wav', 'http://audio.norijacoby.com/stims/melodies_female/NC08s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/NC10s.female.n.7.wav', 'http://audio.norijacoby.com/stims/melodies_female/NC12s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/NC14s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/NC16s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/NC18s.female.n.8.wav', 'http://audio.norijacoby.com/stims/melodies_female/NC20s.female.n.7.wav', 'http://audio.norijacoby.com/stims/melodies_female/NC22s.female.n.8.wav', 'http://audio.norijacoby.com/stims/melodies_female/NC24s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/NC26s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/NC28s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/NC30s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/NC32s.female.n.8.wav', 'http://audio.norijacoby.com/stims/melodies_female/NC34s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/NC36s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/NC38s.female.n.8.wav', 'http://audio.norijacoby.com/stims/melodies_female/NC40s.female.n.8.wav', 'http://audio.norijacoby.com/stims/melodies_female/NC42s.female.n.8.wav', 'http://audio.norijacoby.com/stims/melodies_female/NC44s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/NC46s.female.n.8.wav', 'http://audio.norijacoby.com/stims/melodies_female/NC48s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/NC50s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/NC52s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/NC54s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/NC56s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/NC58s.female.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_female/NC60s.female.n.9.wav'], 'num_notes': ['6', '6', '7', '9', '9', '9', '9', '9', '9', '9', '9', '9', '9', '9', '8', '9', '8', '9', '8', '9', '9', '9', '9', '9', '9', '8', '9', '9', '9', '9', '8', '8', '8', '9', '7', '9', '9', '9', '8', '7', '8', '9', '9', '9', '9', '8', '9', '9', '8', '8', '8', '9', '8', '9', '9', '9', '9', '9', '9', '9'], 'N_maxtrials': 60, 'description': "1. You will hear a short melody.<br> 2. Immediately after the end of the melody, sing the note you think comes next. <br> 3. Please use the syllable 'la' for singing"}]
    experiments_male=[{'name': 'Game 1: Pitch matching', 'trial_messages': ['Sing the same tone as accurately as possible!', 'Thank you!'], 'N_repetitions': 1, 'stim_list': ['http://audio.norijacoby.com/stims/pitches_male/male.43.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.44.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.45.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.46.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.47.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.48.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.49.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.50.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.51.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.52.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.53.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.54.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.55.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.56.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.57.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.58.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.59.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.60.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.43.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.44.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.45.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.46.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.47.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.48.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.49.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.50.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.51.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.52.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.53.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.54.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.55.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.56.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.57.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.58.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.59.mid.n.1.wav', 'http://audio.norijacoby.com/stims/pitches_male/male.60.mid.n.1.wav'], 'num_notes': ['1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1'], 'N_maxtrials': 36, 'description': "1. You will hear a tone.<br>2. Right after the tone, sing the same tone as accurately as possible. <br> 3. Please use the syllable 'la' for singing"}, {'name': 'Game 2: Continue the melody', 'trial_messages': ['Sing the note you think comes next!', 'Thank you!'], 'N_repetitions': 1, 'stim_list': ['http://audio.norijacoby.com/stims/melodies_male/AC01s.male.n.6.wav', 'http://audio.norijacoby.com/stims/melodies_male/AC03s.male.n.6.wav', 'http://audio.norijacoby.com/stims/melodies_male/AC05s.male.n.7.wav', 'http://audio.norijacoby.com/stims/melodies_male/AC07s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/AC09s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/AC11s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/AC13s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/AC15s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/AC17s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/AC19s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/AC21s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/AC23s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/AC25s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/AC27s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/AC29s.male.n.8.wav', 'http://audio.norijacoby.com/stims/melodies_male/AC31s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/AC33s.male.n.8.wav', 'http://audio.norijacoby.com/stims/melodies_male/AC35s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/AC37s.male.n.8.wav', 'http://audio.norijacoby.com/stims/melodies_male/AC39s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/AC41s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/AC43s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/AC45s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/AC47s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/AC49s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/AC51s.male.n.8.wav', 'http://audio.norijacoby.com/stims/melodies_male/AC53s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/AC55s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/AC57s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/AC59s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/NC02s.male.n.8.wav', 'http://audio.norijacoby.com/stims/melodies_male/NC04s.male.n.8.wav', 'http://audio.norijacoby.com/stims/melodies_male/NC06s.male.n.8.wav', 'http://audio.norijacoby.com/stims/melodies_male/NC08s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/NC10s.male.n.7.wav', 'http://audio.norijacoby.com/stims/melodies_male/NC12s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/NC14s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/NC16s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/NC18s.male.n.8.wav', 'http://audio.norijacoby.com/stims/melodies_male/NC20s.male.n.7.wav', 'http://audio.norijacoby.com/stims/melodies_male/NC22s.male.n.8.wav', 'http://audio.norijacoby.com/stims/melodies_male/NC24s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/NC26s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/NC28s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/NC30s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/NC32s.male.n.8.wav', 'http://audio.norijacoby.com/stims/melodies_male/NC34s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/NC36s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/NC38s.male.n.8.wav', 'http://audio.norijacoby.com/stims/melodies_male/NC40s.male.n.8.wav', 'http://audio.norijacoby.com/stims/melodies_male/NC42s.male.n.8.wav', 'http://audio.norijacoby.com/stims/melodies_male/NC44s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/NC46s.male.n.8.wav', 'http://audio.norijacoby.com/stims/melodies_male/NC48s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/NC50s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/NC52s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/NC54s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/NC56s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/NC58s.male.n.9.wav', 'http://audio.norijacoby.com/stims/melodies_male/NC60s.male.n.9.wav'], 'num_notes': ['6', '6', '7', '9', '9', '9', '9', '9', '9', '9', '9', '9', '9', '9', '8', '9', '8', '9', '8', '9', '9', '9', '9', '9', '9', '8', '9', '9', '9', '9', '8', '8', '8', '9', '7', '9', '9', '9', '8', '7', '8', '9', '9', '9', '9', '8', '9', '9', '8', '8', '8', '9', '8', '9', '9', '9', '9', '9', '9', '9'], 'N_maxtrials': 60, 'description': "1. You will hear a short melody.<br> 2. Immediately after the end of the melody, sing the note you think comes next. <br> 3. Please use the syllable 'la' for singing"}]


    if is_female:
        experiments=experiments_female
        # (exp1_stim_list,exp1_num_notes)=get_urls_num_notes('stims/pitches_female',2)
        # (exp2_stim_list,exp2_num_notes)=get_urls_num_notes('stims/melodies_female',1)
    else:
        experiments=experiments_male
        # (exp1_stim_list,exp1_num_notes)=get_urls_num_notes('stims/pitches_male',2)
        # (exp2_stim_list,exp2_num_notes)=get_urls_num_notes('stims/melodies_male',1)

    # experiments=[exp1, exp2]
    params={'experiments': experiments}
    ## use title name < you allready have it>
    ## use instrcution
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


def send_analyze(wfile,participant_id='anonym'):
    params=dict()
    done_ext='html'

    url='http://audio.norijacoby.com/analyze'
    mscript='detect_pitch_in_file_web'
    session_id=str(random.randint(1000,10000))
    file_id=str(random.randint(1000,10000))
    return_route='http://audio.norijacoby.com/set_analysis_response' #the url should have the following form http:/xxx/boo/is_sucess/done-fname
    sver=aver

    params.update({'url':url,'mscript':mscript, 'session_id':session_id, 'file_id': file_id, 'return_route': return_route,'ver':sver, 'done_ext':done_ext, 'participant_id':participant_id})

    return do_analyze(wfile,params)


def do_analyze(wfile, params):

    print "reading params..."
    sver=params['ver']
    session_id=params['session_id']
    file_id=params['file_id']
    print "HERE3"
    done_ext=params['done_ext']
    url=params['url']
    participant_id=params['participant_id']


    print "setting params..."
    rfilename =  sver + '.participant.'+ participant_id +  '.session.' + str(session_id) + '.file.' + str(file_id) +  '.rec'  + '.wav'
    pfilename = sver + '.participant.'+ participant_id + '.session.' + str(session_id) + '.file.' + str(file_id)  + '.todo' + '.json'
    mlogfilename =  sver + '.participant.'+ participant_id + '.session.' + str(session_id) + '.file.' + str(file_id)  + '.mlog' + '.txt'
    donefilename =  sver + '.participant.'+ participant_id + '.session.' + str(session_id) + '.file.' + str(file_id)  + '.done.' + done_ext


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
    return render_template('MelodyGame3.html')



@app.route('/getAudioFileName', methods = ['GET'])
def getAudioFileName_route():
    #print("here...")
    filename='http://audio.norijacoby.com/stims/stim1.ogg'
    print ("got a get request returning filename: " + filename)
    out= json.dumps({"fname": filename})
    print out
    return Response(out, status=200, mimetype='application/json')

## no participant ID...
@app.route('/upload/', methods = ['POST'])
def upload_route(participant_id):
    try:
        if request.method == 'POST':
            wfile = request.files['file']
            print "about to  sent: "
            return send_analyze(wfile)
    except Exception as e:
        print(e)

## no participant ID...
@app.route('/uploadP/<participant_id>', methods = ['POST'])
def upload_routeP(participant_id):
    try:
        if request.method == 'POST':
            wfile = request.files['file']
            print "about to  sent: "
            return send_analyze(wfile,participant_id)
    except Exception as e:
        print(e)

@app.route('/saveOnSever/<participant_id>/<file_name>', methods = ['POST'])
def saveOnSever(participant_id,file_name):
    try:
        print ('Save on server start...')
        #session_id=str(random.randint(1000,10000))
        #file_id=str(random.randint(1000,10000))
        session_id='0000' #save only once
        file_id=file_name
        url=burl_audio + '/saveOnSever'
        serverfilename =  aver + '.participant.'+ participant_id + '.session.' + str(session_id) + '.file.' + str(file_id)  + '.json' + '.html'
        print request.method
        print request
        if request.method == 'POST':
            mdata = request.data
            print mdata
            print ('SaveOnServer-getting things...')
            wfile = StringIO.StringIO(mdata)
            if wfile is None:
                wfile = StringIO.StringIO("<empty>")
            files = {'rec': (serverfilename , wfile)}

            print('trying to send...')
            r = requests.post(url, files=files)

            print('OK response... :' + r.text)
            return r.text
    except Exception as e:
        print(e)

 # pfile = StringIO.StringIO(json.dumps(params))
 #    if wfile is None:
 #        wfile = StringIO.StringIO("<empty>")

 #    # if fileNone is None:
 #    #     files = {'rec': (rfilename, file), 'param': (pfilename,pfile)}
 #    # else:
 #    #     files = {'rec': (rfilename, file), 'param': (pfilename,pfile)}

 #    files = {'rec': (rfilename, wfile), 'param': (pfilename,pfile)}

 #    print('trying to send...')
 #    r = requests.post(url, files=files)
 #    pfile.close()
 #    print('OK response... :' + r.text)
 #    return r.text_file


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


@app.route('/get_params/<participant_id>/<is_female>', methods = ['GET'])
def get_params(participant_id,is_female):
    print "tryig to get params... female=" + is_female
    params=['stam'];
    params=init_params(int(is_female)==0)
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

