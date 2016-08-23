#general imports
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
import traceback


# wallace imports
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

#time imports
from datetime import datetime
from dateutil import parser as time_parser
import time


config = PsiturkConfig()


GLOBAL_PARAMS= {'duration': 2,'range_min':60, 'range_max':65, 'status_min_times':[5,10,20,25,30,9999]}
FULLY_ADVANCED_STATUS=5
#  transformation1 = SubstitutionCipher(info_in=info, node=self)
#            transformation1.apply()

burl_res='http://audio.norijacoby.com/res/'
server_url='http://audio.norijacoby.com/'
burl_res='http://audio.norijacoby.com/res/'
aver='WA1'

class AudioExperiment(Experiment):

    def __init__(self, session):
        super(AudioExperiment, self).__init__(session)

        self.N_network_size=5  #%number of networks
        self.N_network_size_practice=5 #%number of practice networks
        self.K_repeats_size=2 #%hie much trials each subject play
        self.K_repeats_size_practice=2 #%how much practice trials each subject has
        self.M_length=3 #% length of chain
        self.K_all_trials=self.K_repeats_size+self.K_repeats_size_practice


        """ Wallace parameters """
        self.task = "The Audio Game"
        self.verbose = False
        self.experiment_repeats = self.N_network_size  # N number of chains
        self.practice_repeats = self.N_network_size_practice    # N number of chains for practice

        #self.agent = AudioAgent
        self.network = lambda: MultiChain(max_size=self.M_length)

        self.initial_recruitment_size = 10 # initital recuriemnt size (number of participants initally recruited) ##IMPORTANT THIS SHOULD BE more than 10 becuase if not you only have 10 subjects.
        self.instruction_pages = ["instructions/instruct-1.html"]
        self.debrief_pages = ["debriefing/debrief-1.html"]
        self.known_classes["AudioInfo"] = AudioInfo
        self.known_classes["AudioSource"] = AudioSource


        if not self.networks():
            self.setup()
        self.save()

    def node_type(self, network):
        return AudioAgent

    def get_network_for_participant (self, participant):
        # get the participants nodes
        node_participated = Node.query.filter_by(participant_id=participant.id).all()
        # get all the networks
        all_networks = Network.query.all()

        # get the networks that the participant has participated in
        network_participated_ids = [n.network_id for n in node_participated]
        network_participated = [n for n in all_networks if n.id in network_participated_ids]

        # get the networks that are currently open
        open_networks = [n for n in all_networks if n.open and not n.full]

        # get the open and unparticipated networks
        possible_networks = [net for net in open_networks if net.id not in network_participated_ids]

        # how many practice networks have they participated in
        num_practice_participated = len([n for n in network_participated if n.role == "practice"])

        # if they can keep practicing
        if (num_practice_participated < self.K_repeats_size_practice):
            possible_networks = [net for net in possible_networks if net.role == "practice"]
        else:
            # how many test networks have they participated in
            num_test_participated = len([n for n in network_participated if n.role != "practice"])
            # if they can keep going
            if (num_test_participated < self.K_repeats_size):
                possible_networks = [net for net in possible_networks if net.role != "practice"]
            else:
                return None

        if possible_networks:
            chosen_network = random.choice(possible_networks)
        else:
            return None


        chosen_network.open = False
        return chosen_network

    def node_post_request(self, participant, node):
        node.neighbors(connection="from")[0].transmit()
        node.receive()

    def info_post_request(self, node, info):
        try:
            res = int(info.contents)
        except:
            node.fail()
        #node.network.open = True # this is only open when node advanced to status=5


    def setup(self):
        super(AudioExperiment, self).setup()
        for net in self.networks():
            if net.role == "practice":
                net.max_size = 500
            source = AudioSource(network=net)
            source.create_pattern(self.range_min, self.range_max)
            source.generation = 0
            #net.open = True


    def recruit(self):
        # participants = Participant.query.with_entities(Participant.status).all()

        # if all network are full close recruitment
        if not self.networks(full=False, role="experiment"):
             self.log("all networks full, closing recruitment")
             self.recruiter().close_recruitment()
        else:
            # ##### NORI ADD THIS DON"T
            # networks = Network.query.all()
            # remaining_nodes=0;
            # for net in networks:
            #     if net.role == "practice":
            #         continue
            #     remaining_nodes=remaining_nodes + Max(net.max_size-len(net.nodes(type=Agent)),0)
            # # to make the logic

            self.recruiter().recruit_participants(n=1)
        #     self.log("generation not finished, not recruiting")

        # advances all infos in all networks
        def advance_all_infos (self):
            # get all the networks
            #all_networks = Network.query.all()
            nodes = AudioAgent.query.filter_by(failed=False).all()

            count_advanced_nodes= 0
            count_failed_nodes= 0
            count_ignored_nodes= 0

            for node in nodes:
                resp=node.AdvanceNode()
                if resp==1:
                    count_advanced_nodes=count_advanced_nodes+1
                if resp==-1:
                    count_failed_nodes=count_failed_nodes+1
                if resp==0:
                    count_ignored_nodes=count_ignored_nodes+1

            print "finished advancing all possible nodes. advanced nodes = {} failed nodes = {} ignored nodes ={}".format(count_advanced_nodes,count_failed_nodes,count_ignored_nodes)
            return count_advanced_nodes

    def data_check(self, participant):
              # get the necessary data
        networks = Network.query.all()
        nodes = AudioAgent.query.filter_by(participant_id=participant.id, failed=False).all()
        node_ids = [n.id for n in nodes]
        incoming_vectors = Vector.query.filter(Vector.destination_id.in_(node_ids)).all()
        outgoing_vectors = Vector.query.filter(Vector.origin_id.in_(node_ids)).all()

        try:
            # 1 source node per network
            for net in networks:
                sources = net.nodes(type=AudioSource)
                assert len(sources) == 1
                 # only one source for every network


            # 1 vector (incoming) per node
            for node in nodes:
                try:
                    assert len([v for v in outgoing_vectors if v.origin_id == node.id and not v.failed]) in [0,1]
                    assert len([v for v in incoming_vectors if v.destination_id == node.id]) == 1
                except:
                    print "Warning: problem with number of vectors (a)= " + str(len([v for v in outgoing_vectors if v.origin_id == node.id and not v.failed])) + " (b)= " + str(len([v for v in incoming_vectors if v.destination_id == node.id]))
                    node.fail()

                ## not failed nodes???? PERHAPS FILTER HERE OVER NOT FAILED NODES? IS IT AUDIO?
                infos =  node.infos(AudioInfo)
                #print ([type(i) for i in  infos])
                ################### NORI #################
                ###original:
                ### assert (len([i for i in infos ]) == 1)

                #implement some checks on transmisision and transformation
                # so far not implemented
                # if (len([i for i in infos ]) != 1):
                #     node.fail()
                # else:
                #     info=infos[0]
                #     ResponseRatio=info.contents
                #     TrueRatio=info.true_seed
                #     is_numeric = False
                #     try:
                #         ResponseRatio=int(info.contents)
                #         is_numeric = True
                #     except:
                #         pass

                #     #implement this part
                #     # if is_numeric:
                #     #     assert (abs(ResponseRatio-TrueRatio)<=self.UI_PROX_T)
                #     # else:
                #     #     assert (ResponseRatio=='NaN')

                #     try:
                #         assert len(node.transmissions(direction="all", status="pending")) == 0
                #         assert len(node.transmissions(direction="incoming", status="received")) == 1
                #     except:
                #         print "Warning: had to fail nodes because of transmission error"
                #         node.fail()

            self.log("Data check passed!")
            return True
        except:
            import traceback
            traceback.print_exc()
            return False


    def bonus(self, participant):
#         tried_attempts=0
#         good_trials=0
#         overall_attempts=0;
#         failed_nodes=0;
#         not_good_trials=0;
#         nodes = AudioAgent.query.filter_by(participant_id=participant.id).all()
#         for node in nodes:
#             if node.failed:
#                 failed_nodes+=1
#                 tried_attempts+=1
#             else:
# #                infos = node.infos(type=AudioInfo )
#                 infos = node.infos()
#                 for info in infos:
#                     tried_attempts+=1
#                     try:
#                         num_attempts=int(info.property1)
#                         #num_attempts=info.num_attempts
#                     except:
#                         num_attempts=0
#                     if num_attempts==1:
#                         good_trials+=1
#                     if num_attempts>1:
#                         not_good_trials+=1
#         #self.log("\NORITHERE-len(nodes)= {} self.K_all_trials={} good_trials={}  failed_nodes={}".format(len(nodes),self.K_all_trials,good_trials,failed_nodes))
#         score =  (0.2*len(nodes))/self.K_all_trials  + (0.8*good_trials)/self.K_all_trials #+ 0.2*(good_trials - failed_nodes ) * 1.0 / (tried_attempts)
#         #score =  (1.0*good_trials)/self.K_all_trials
#         score = score - 0.8*failed_nodes/self.K_all_trials - 0.5*not_good_trials/self.K_all_trials
#         #score = round(score*100.0)/100.0
# #        score = score*0.5 + 0.5
#         #score = (good_trials - failed_nodes) * 1.0 / (tried_attempts)
#         score = max (score, 0.02)
#         score = min (score, 0.95)

#         #if tried_attempts<5:
#         #    score=0.10
#         to_return_score=round(score*self.bonus_payment*100.0)/100.0
#         return to_return_score
          return 0.5;


    def attention_check(self, participant):

 #        # how to retrieve failes nodes?
 #        tried_attempts=0
 #        tried_trials=0
 #        failed_nodes=0;
 #        nodes = AudioAgent.query.filter_by(participant_id=participant.id).all()
 #        for node in nodes:
 #            if node.failed:
 #                failed_nodes+=1
 #            else:
 #                infos =  node.infos(type=AudioInfo )
 #                for info in infos:
 #                     tried_attempts+=info.num_attempts
 #                     tried_trials+=1
 #        #print ("ATTENTION CHECK: failed_nodes:" + str(failed_nodes) + " tried_attempts: " + str(tried_attempts) + "tried_trials" + str(tried_trials))
 #        print "ATTENTION: tried_attempts: " + str(tried_attempts)
 #        print "ATTENTION: self.Percent_attention_trials: " + str(self.Percent_attention_trials)
 #        print "ATTENTION: tried_trials: " + str(tried_trials)

 #        if (tried_attempts*100>self.Percent_attention_trials*tried_trials):
 #            print "ATTENTION: failed attention test 1"
 #            return False
 # #       failed_nodes=len(Node.query.filter_by(failed=True,participant_id=participant.id).all())
 #        print "ATTENTION: passed attention test 1"
 #        print "ATTENTION: failed_nodes: " + str(failed_nodes)
 #        print "ATTENTION: Percent_failed_nodes: " + str(self.Percent_failed_nodes)
 #        print "ATTENTION: len(nodes): " + str(len(nodes))

 #        #note that this should only apply when you have enought trials this is why tried_trials is suppose to be large (e.g >4)
 #        if ((100*failed_nodes>self.Percent_failed_nodes*len(nodes))):
 #            print "ATTENTION: failed attention test 2"
 #            return False
 #        print "ATTENTION: passed attention test (all)"
        return True
########################### NORIHERE ################################

########################### NORIHERE ################################



class MultiChain(Chain):

    __mapper_args__ = {"polymorphic_identity": "multi_chain"}

    @hybrid_property
    def open(self):
        return bool(self.property1)

    @open.setter
    def open(self, open):
        self.property1 = repr(open)

    @open.expression
    def open(self):
        return cast(self.property1, Boolean)

    def add_node(self, newcomer):
        super(MultiChain, self).add_node(newcomer)
        prev_agents = type(newcomer).query\
                .filter_by(failed=False,
                           network_id=self.id,
                           )\
                .all()

        if prev_agents:
            previous_generation=max([p.generation for p in prev_agents]) + 1
        else:
            previous_generation=0
        newcomer.generation = previous_generation



class AudioSource(Source):
    """ A source that initializes the pattern of the first generation """

    def _what(self):
        return AudioSource

    def create_pattern(self, range_min, range_max):
    #     #AudioInfo (origin=self, contents=random.randint(0,100));
        print ("trying to create pattern... for source id {}:", self.id)
        info=AudioInfo(origin=self, contents=None)
        info.contents=info.create_random_contents()
        info.status = 3
        #info.file_id = info.create_new_file_id()
        info.file_id = None #because replaced in status 3
        info.root_creation_time = info.creation_time
        info.generation = 0

    @hybrid_property
    def generation(self):
        if not self.property1:
            return 0
        return int(self.property1)

    @generation.setter
    def generation(self, generation):
        self.property1 = repr(generation)

    @generation.expression
    def generation(self):
        return cast(self.property1, Integer)

    __mapper_args__ = {"polymorphic_identity": "audio_source"}

    def _what(self):
        return AudioInfo

    def AdvanceNode(self):
        status_min_times=GLOBAL_PARAMS['status_min_times']
        infos =  self.infos(AudioInfo)
        last_status=max([info.status for info in infos]) # the last status info for this node
        for info in infos:
            status= info.status
            # make sure this is the last status
            if status<last_status:
                continue

            status_max_time_for_this_stage=status_min_times[status]
            status_max_time_for_all_stages=status_min_times[FULLY_ADVANCED_STATUS]

            delta_time=(datetime.now()-info.root_creation_time).seconds
            #if too much time had passes fail the node!
            if delta_time>status_max_time_for_all_stages:
                print ("too much time passed, failing node!")
                self.fail
                Return (-1)
            #if waiting time of this node had passed adn the node is not fully advanced
            if delta_time>status_max_time_for_this_stage and info.status<FULLY_ADVANCED_STATUS:
                try:
                    print 'trying to advance node_id: {} info_id: {}'.format(self.id,info.info_id)
                    resp=info.Advance()
                    print 'advance node_id: {} info_id: {} was: {}'.format(self.id,info.info_id,resp)
                    if resp:
                        return 1
                except:
                    print 'failed advancing node_id:{} info_id: {}'.format(self.id,info.info_id)
                    traceback.print_exc()
                    return 0
        return 0


class AudioAgent(Agent):
    def fail(self, vectors=True, infos=True, transmissions=True, transformations=True):
        """
        Fail a node, setting its status to "failed".

        Also fails all vectors that connect to or from the node.
        You cannot fail a node that has already failed, but you
        can fail a dead node.
        """

        if self.failed is True:
            #raise AttributeError(
            print " Warning: Cannot fail {} - it has already failed.".format(self)
        else:
            self.failed = True
            self.time_of_death = datetime.now()
            for n in self.neighbors(): ##
                n.fail()
                self.network.open= False

            if self.network is not None:
                self.network.calculate_full()

            if vectors:
                for v in self.vectors():
                    v.fail()
            if infos:
                for i in self.infos():
                    i.fail()
            if transmissions:
                for t in self.transmissions(direction="all"):
                    t.fail()
            if transformations:
                for t in self.transformations():
                    t.fail()

    def AdvanceNode(self):
        status_min_times=GLOBAL_PARAMS['status_min_times']
        infos =  self.infos(AudioInfo)
        last_status=max([info.status for info in infos]) # the last status info for this node
        for info in infos:
            status= info.status
            # make sure this is the last status
            if status<last_status:
                continue

            status_max_time_for_this_stage=status_min_times[status]
            status_max_time_for_all_stages=status_min_times[FULLY_ADVANCED_STATUS]

            delta_time=(datetime.now()-info.root_creation_time).seconds
            #if too much time had passes fail the node!
            if delta_time>status_max_time_for_all_stages:
                print ("too much time passed, failing node!")
                self.fail
                Return (-1)
            #if waiting time of this node had passed adn the node is not fully advanced
            if delta_time>status_max_time_for_this_stage and info.status<FULLY_ADVANCED_STATUS:
                try:
                    print 'trying to advance node_id: {} info_id: {}'.format(self.id,info.info_id)
                    resp=info.Advance()
                    print 'advance node_id: {} info_id: {} was: {}'.format(self.id,info.info_id,resp)
                    if resp:
                        return 1
                except:
                    print 'failed advancing node_id:{} info_id: {}'.format(self.id,info.info_id)
                    traceback.print_exc()
                    return 0
        return 0
        #self.network.open= True #because the network might be stuck #this no longer done here because
        #we need to open only after preperation of new data

    """ A source that initializes the pattern of the first generation """
    @hybrid_property
    def generation(self):
        if not self.property1:
            return 0
        return int(self.property1)

    @generation.setter
    def generation(self, generation):
        self.property1 = repr(generation)

    @generation.expression
    def generation(self):
        return cast(self.property1, Integer)



    __mapper_args__ = {"polymorphic_identity": "audio_agent"}

    def _what(self):
        return AudioInfo  ### QUESTION TOMAS??? OR AudioAgent


extra_routes = Blueprint(
    'extra_routes', __name__,
    template_folder='templates',
    static_folder='static')



def date_handler(obj):
    """Serialize dates."""
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj


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
            print ("this info is fully advanced...")
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
            self.network.open = True # this node is fully advanced! you can now open the network for participation

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


# @extra_routes.route("/is_practice/<int:network_id>", methods=["GET"])
# def get_is_practice(network_id):
# #    exp = AudioExperiment(db.session)
#     net=Network.query.get(network_id)
#     data = {"status": "success", "is_practice": net.role == "practice"}
#     return Response(dumps(data), status=200, mimetype='application/json')


# @extra_routes.route("/trial_number_string/<int:node_id>/<int:participant_id>", methods=["GET"])
# def get_trial_number_string(node_id,participant_id):
#     exp = AudioExperiment(db.session)
#     node = AudioAgent.query.get(node_id)
#     participants = Participant.query.filter_by(id=participant_id).all()
#     bonus=exp.bonus(participants[0])

#     exp.log("/trial_number_string GET request. Params: node_id: {}."
#             .format(node_id))

#     # check the node exists for the current particiapnt
#     nodes = len(AudioAgent.query.filter_by(participant_id=node.participant_id).all())
#     all_trials=exp.K_all_trials

#     if node is None:
#         exp.log("Error: /trial_number_string/{}, node {} does not exist".format(node_id, node_id))
#         page = error_page(error_type="/trial_number_string, node does not exist")
#         js = dumps({"status": "error", "html": page})
#         return Response(js, status=400, mimetype='application/json')

#     # return the data
#     data = str(nodes) + " / " + str(all_trials) + ". Estimated bonus so far: " + str(bonus) + "$"
#     data = {"status": "success", "trial_str": data, "generation": node.generation}
#     exp.log("/trial_number_string GET request successful.")
#     js = dumps(data, default=date_handler)
#     return Response(js, status=200, mimetype='application/json')


