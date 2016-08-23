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

GLOBAL_PARAMS= {'duration': 2}
#  transformation1 = SubstitutionCipher(info_in=info, node=self)
#            transformation1.apply()

burl_res='http://audio.norijacoby.com/res/'
server_url='http://audio.norijacoby.com/'
burl_res='http://audio.norijacoby.com/res/'
aver='WA1'



class AudioInfo(Info)
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

    # data (2)
    @hybrid_property
    def data(self):
        return str(self.data)

    @status.setter
    def data(self, data):
        self.property2 = repr(data)

    @status.expression
    def data(self):
        return cast(self.property2, String)

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
        cmd=server_url+"/is_file_exists/" + filename
        print ('trying to run this cmd to server: '+ cmd)
        r = requests.get(cmd)
        print('For file:' + filename + ', I got from server OK response... :' + r.text)
        return r.text

    def create_file_names(self):
        file_id=self.file_id
        my_net_id=self.network_id
        session_id=my_net_id*1000 + ((1754517*my_net_id+743) % 1000) # pseudocrypto
        audio_filename =  aver + '.session.' + str(session_id) + '.file.' + str(file_id) +  '.rec'  + '.wav'
        data_filename =  aver + '.session.' + str(session_id) + '.file.' + str(file_id)  + '.done.' + 'html'

        all_filename={'audio_file_name': audio_filename, 'data_filename':data_filename,'file_id':file_id,'session_id':session_id}
        return all_filename


    def check_audio_file_exists(self):
        all_filename=self.create_file_names()
        return self.check_file_exists(all_filename['audio_filename']):

    ## compute filename from internal content, than ping a route that says if the file exists.
    def check_data_file_exists(self):
       return self.check_file_exists(all_filename['data_filename']):

    def create_new_file_id(self): # status is leading 10xxxxx and than some random number
        self.file_id=random.randint(0,10000)

    def upload_file(self,audio_file): # take the information in the info and the audio file and upload it to server
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
        return check_data_file_exists(self)

    def create_new_stimulus(self): #create new stimulus on the output server
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
    def modify_data(self,my_data): #rules for how to change data (experiment specific)
        self.data=my_data # at the moment just copy data

    def do_analyze(self,wfile, params):

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




#     """A simulated agent that applies a substitution cipher to the text."""

#     __mapper_args__ = {"polymorphic_identity": "simulated_agent"}

#     def update(self, infos):
#         for info in infos:
#             # Apply the translation transformation.
#             transformation1 = SubstitutionCipher(info_in=info, node=self)
#             transformation1.apply()

class AdvanceStatus(Transformation):
    """Advance the status of a node"""

    __mapper_args__ = {"polymorphic_identity": "AdvanceStatus_tranformation"}


    def apply(self, audio_file=None):
        childrens=self.info_in.transformations(relationship="parent")

        if(len(childrens)==0):  #if you have allready advanved this just exit
            print("this node was allready advanced...")
            return False

        my_status = self.info_in.status
        my_data = self.info_in.data
        my_file_id=self.info_in.file_id
        my_root_creation_time=self.info_in.creation_time
        my_generation=self.info_in.generation

        # stimulus and files prepared, now check they are really there, this is the
        if my_status==0: #check that stimulus/data files are ready (created)
        #in status 1 you are suppose to be able to run.

            assert(self.info_in.check_audio_file_exists()) ## compute filename from internal content, than ping a route that says if the file exists.
            assert(self.info_in.check_data_file_exists()) ## compute filename from internal content, than ping a route that says if the file exists.


        # just got data from subejct, create a new file id and upload it, get the confirmation status,
        #in this status you wait for analyis.
        if my_status ==1:
            assert(audio_file is not None) # assert audio_file is not none, because to move to status 1

            my_file_id= self.info_in.create_new_file_id() # status is leading 10xxxxx and than some random number

            resp=self.info_in.upload_file(audio_file) # take the information in the info and the audio file and upload it to server

            assert(resp.success) # see that the response was sucessful

        #check that analyis is ready if not just quit.
        if my_status ==2:
            if not self.info_in.check_analsys_file_exists():
                return False
            my_data=self.info_in.get_data_from_server() # get analyzed data from server

        #modify the data, do not do futher things (will be done AFTER creation of the new info)
        if my_status ==3:
            my_data=self.info_in.modify_data(my_data)
            my_file_id= self.info_in.create_new_file_id() # status is leading 10xxxxx and than some random number


        #to move to the final status you should have a valid (new) stimulus file (and then ALSO data file)
        if my_status ==4:
            if not self.check_audio_file_exists():
                return False

            assert(self.info_in.check_data_file_exists()) ## compute filename from internal content, than ping a

        #creat the info_out
        info_out = AudioInfo(origin=self.node)
        info_out.status = my_status+1
        info_out.data  = my_data
        info_out.file_id = my_file_id
        info_out.root_creation_time = my_root_creation_time
        info_out.generation = my_generation
        self.info_out = info_out

        #create the new data (should corresopond to the modified data)
        if my_status ==3:
            resp=self.info_out.create_new_stimulus()
            assert(resp)


        return True
