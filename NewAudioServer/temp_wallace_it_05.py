import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, Blueprint, Response, request, render_template
from werkzeug import secure_filename
import random
from json import dumps
import os
import requests
import shutil
import socket
import StringIO
import urllib2

from wallace.experiments import Experiment
from wallace.nodes import Agent, Source
from wallace.models import Info, Network, Vector, Node, Participant, Transformation
from wallace.networks import Chain
from wallace.information import Gene
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.expression import cast
from sqlalchemy import Integer, Float
from psiturk.psiturk_config import PsiturkConfig
from wallace import db
config = PsiturkConfig()
from datetime import datetime


GLOBAL_PARAMS= {'duration': 2,'range_min':60, 'range_max':65}
#  transformation1 = SubstitutionCipher(info_in=info, node=self)
#            transformation1.apply()

burl_res='http://audio.norijacoby.com/res/'
server_url='http://audio.norijacoby.com/'
burl_res='http://audio.norijacoby.com/res/'
aver='WA1'




class AudioSource(Source):
    """ A source that initializes the pattern of the first generation """

    def _what(self):
        return AudioSource

    def create_pattern(self, range_min, range_max):
    #     #LineInfo(origin=self, contents=random.randint(0,100));
        info=AudioInfo(origin=self, contents=None)
        info.contents=info.create_random_contents()
        info.status = 3
        #info.file_id = info.create_new_file_id()
        info.file_id = None #because replaced in status 3
        info.root_creation_time = info.creation_time
        info.generation = 0


class AudioInfo(Info):
    __mapper_args__ = {"polymorphic_identity": "audio_info"}

   # status (1)
    @hybrid_property
    def status(self):
        return int(self.status)

    @status.setter
    def status(self, status):
        self.property1 = repr(status)

    @status.expression
    def status(self):
        return cast(self.property1, Integer)


    # file_id (3)
    @hybrid_property
    def file_id(self):
        return str(self.file_id)

    @status.setter
    def file_id(self, file_id):
        self.property3 = repr(file_id)

    @status.expression
    def file_id(self):
        return cast(self.property3, String)

    # root_creation_time (4)
    @hybrid_property
    def root_creation_time(self):
        return int(self.root_creation_time)

    @status.setter
    def root_creation_time(self, root_creation_time):
        self.property4 = repr(root_creation_time)

    @status.expression
    def root_creation_time(self):
        return cast(self.property4, String)

    # generation (5)
    @hybrid_property
    def generation(self):
        if self.property5:
            return int(self.property5)
        else:
            return 0

    @generation.setter
    def generation(self, my_generation):
        self.property5 = repr(my_generation)

    @generation.expression
    def generation(self):
        return cast(self.property5, Integer)

    ## compute filename from internal content, than ping a route that says if the file exists.
    def check_file_exists(self,filename):
        print ("INFO-METHOD: check_file_exists")
        cmd=server_url+"/is_file_exists/" + filename
        print ('trying to run this cmd to server: '+ cmd)
        r = requests.get(cmd)
        print('For file:' + filename + ', I got from server OK response... :' + r.text)
        return r.text

    def create_file_names(self):
        print ("INFO-METHOD: create_file_names")
        file_id=self.file_id
        my_net_id=self.network_id
        session_id=my_net_id*1000 + ((1754517*my_net_id+743) % 1000) # pseudocrypto
        audio_filename =  aver + '.session.' + str(session_id) + '.file.' + str(file_id) +  '.rec'  + '.wav'
        data_filename =  aver + '.session.' + str(session_id) + '.file.' + str(file_id)  + '.done.' + 'html'

        all_filename={'audio_file_name': audio_filename, 'data_filename':data_filename,'file_id':file_id,'session_id':session_id}
        return all_filename


    def check_audio_file_exists(self):
        print ("INFO-METHOD: check_audio_file_exists")
        all_filename=self.create_file_names()
        return self.check_file_exists(all_filename['audio_filename'])

    ## compute filename from internal content, than ping a route that says if the file exists.
    def check_data_file_exists(self):
        print ("INFO-METHOD: check_data_file_exists")
        return self.check_file_exists(all_filename['data_filename'])

    def create_new_file_id(self): # status is leading 10xxxxx and than some random number
        print ("INFO-METHOD: create_new_file_id")
        return random.randint(0,9999)+self.status*10000

    def upload_file(self,audio_file): # take the information in the info and the audio file and upload it to server
        print ("INFO-METHOD: upload_file")
        mscript='detect_pitch_in_file_web'
        return_route='http://audio.norijacoby.com/set_analysis_response' #the url should have the following form
        url='http://audio.norijacoby.com/analyze'
        all_filename=self.create_file_names()
        done_ext='html'
        file_id=all_filename['file_id']
        session_id=all_filename['session_id']
        sver=aver

        params={'url':url,'mscript':mscript, 'session_id':session_id, 'file_id': file_id, 'return_route': return_route,'ver':sver, 'done_ext':done_ext}

        return self.do_analyze(audio_file,params)


    def check_analsys_file_exists(self):  #check that analyis is ready (note that this is the data file)
        print ("INFO-METHOD: check_analsys_file_exists")
        return check_data_file_exists(self)

    def create_new_stimulus(self): #create new stimulus on the output server
        print ("INFO-METHOD: create_new_stimulus")
        url='http://audio.norijacoby.com/analyze'
        mscript='pitch_stim_create'
        return_route='http://audio.norijacoby.com/boo' #the url should have the following form
        midi=data

        print "try_to_create_pitch: " + str(midi)
        all_filename=self.create_file_names()

        params=dict()
        params.update( {'midi': midi, 'duration':GLOBAL_PARAMS['duration']})
        done_ext='ogg'

        wfile=None
        file_id=self.file_id
        my_net_id=self.network_id
        session_id=my_net_id*1000 + ((1754517*my_net_id+743) % 1000) # pseudocrypto

        sver=aver
        params.update({'url':url, 'mscript':mscript, 'session_id':session_id, 'file_id': file_id, 'return_route': return_route,'ver':sver, 'done_ext':'ogg' })
        print params
        return self.do_analyze(wfile,params)


    def get_data_from_server(self): # get analyzed data from server
        print ("INFO-METHOD: get_data_from_server")
        murl=burl_res+rfile
        print "trying to get result file: " + murl

        try:
            data = requests.get(murl)
            print "read_data"
            print data
        except Exception as e:
            print(e)
        return Response(data.text, status=200, mimetype='application/html')

    #very specific to the experiment consider putting it as a service function of the experiment
    def modify_data(self): #rules for how to change data (experiment specific)
        print ("INFO-METHOD: modify_data")
        mydata2=self.contents
        return mydata2 # at the moment just copy data

    def create_random_contents(self):
        print ("INFO-METHOD: create_random_contents")
        return random.randint(GLOBAL_PARAMS['range_min'],GLOBAL_PARAMS['range_max'])

    def do_analyze(self,wfile, params):
        print ("INFO-METHOD: do_analyze")
        print "reading params..."
        sver=params['ver']
        session_id=params['session_id']
        file_id=params['file_id']
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

        print "preparing files..."

        pfile = StringIO.StringIO(dumps(params))
        if wfile is None:
            wfile = StringIO.StringIO("<empty>")


        files = {'rec': (rfilename, wfile), 'param': (pfilename,pfile)}

        print('trying to send...')
        r = requests.post(url, files=files)
        pfile.close()
        print('OK response... :' + r.text)
        return r.text

    def Advance(self):
        print ("INFO-METHOD: Advance")
        childrens=self.transformations(relationship="parent")

        if(len(childrens)==0):  #if you have allready advanved this just exit
            print("this node was allready advanced...")
            return None

        my_status = self.status
        my_contents = self.contents
        my_file_id=self.file_id
        my_root_creation_time=self.creation_time
        my_generation=self.generation

        assert(my_status<=5)
        if my_status==5:
            print ("this ninfo is fully advanced...")
            return None

        # stimulus and files prepared, now check they are really there, this is the
        if my_status==0: #check that stimulus/data files are ready (created)
        #in status 1 you are suppose to be able to run.

            assert(self.check_audio_file_exists()) ## compute filename from internal content, than ping a route that says if the file exists.
            assert(self.check_data_file_exists()) ## compute filename from internal content, than ping a route that says if the file exists.


        # just got data from subejct, create a new file id and upload it, get the confirmation status,
        #in this status you wait for analyis.
        if my_status ==1:
            assert(audio_file is not None) # assert audio_file is not none, because to move to status 1

            my_file_id= self.create_new_file_id() # status is leading 10xxxxx and than some random number

            resp=self.upload_file(audio_file) # take the information in the info and the audio file and upload it to server

            assert(resp.success) # see that the response was sucessful

        #check that analyis is ready if not just quit.
        if my_status ==2:
            if not self.check_analsys_file_exists():
                return None
            my_contents=self.get_data_from_server() # get analyzed data from server

        #modify the data, do not do futher things (will be done AFTER creation of the new info)
        if my_status ==3:
            my_contents=self.modify_data()
            my_file_id= self.create_new_file_id() # status is leading 10xxxxx and than some random number


        #to move to the final status you should have a valid (new) stimulus file (and then ALSO data file)
        if my_status ==4:
            if not self.check_audio_file_exists():
                return None

            assert(self.check_data_file_exists()) ## compute filename from internal content, than ping a

        #creat the info_out
        info_out = AudioInfo(origin=self.node, contents=my_contents)
        info_out.status = my_status+1
        info_out.file_id = my_file_id
        info_out.root_creation_time = my_root_creation_time
        info_out.generation = my_generation


        #create the new data (should corresopond to the modified data)
        if my_status ==3:
            resp=self.info_out.create_new_stimulus()
            assert(resp)

        my_transformation = AdvanceStatus(info_in=self, info_out=info_out)


        return my_transformation



class AdvanceStatus(Transformation):
    """Advance the status of an info"""
    __mapper_args__ = {"polymorphic_identity": "AdvanceStatus_tranformation"}

###
###


