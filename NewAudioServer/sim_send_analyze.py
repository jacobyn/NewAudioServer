import os

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, Blueprint, Response, request, render_template
from werkzeug import secure_filename
import random
from json import dumps
import os
import requests
import shutil

mscript='MatlabAnal'
url='http://audio.norijacoby.com/analyze'
url='http://127.0.0.1:5000/analyze'
session_id=str(random.randint(1000,10000))
myrnd=random.randint(1000,10000)
tfname='fileToUpload' +str(myrnd)
filename ='session.'+ session_id + '.script.' + mscript + '.file.' + tfname + '.wav'


file=open("uploads/uploaded1975.wav", 'rb')
files = {'file': (filename, file)}
r = requests.post(url, files=files)
print r.text
print "OK"


