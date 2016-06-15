""" The Lineseg Game! """
""" config for duration of the experiment"""

from wallace.experiments import Experiment
from wallace.nodes import Agent, Source
from wallace.models import Info, Network, Vector, Node, Participant
from wallace.networks import Chain
from wallace.information import Gene
import random
from json import dumps
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.expression import cast
from sqlalchemy import Integer, Float
from flask import Blueprint, Response, request, render_template
import os
from psiturk.psiturk_config import PsiturkConfig
import requests
from wallace import db
config = PsiturkConfig()
from datetime import datetime

class LineGame(Experiment):

    def __init__(self, session):
        super(LineGame, self).__init__(session)
        self.N_network_size=5
        self.N_network_size_practice=3
        self.K_repeats_size=3
        self.K_repeats_size_practice=3
        self.M_length=4

        self.N_network_size=10
        self.N_network_size_practice=5
        self.K_repeats_size=4
        self.K_repeats_size_practice=4
        self.M_length=5

        #these parameters require about 40 subjects with 10 min participation time (need to check how much it takes to run these parameters)
        # self.N_network_size=300
        # self.N_network_size_practice=30
        # self.K_repeats_size=100
        # self.K_repeats_size_practice=10
        # self.M_length=10

        # 3 min ~ 15 participants, 0.5 base payment 0.5 bonus
        ## RUN 5 apr
        # self.N_network_size=20
        # self.N_network_size_practice=20
        # self.K_repeats_size=10
        # self.K_repeats_size_practice=5
        # self.M_length=5
        # self.bonus_payment = 0.5


        # this takes about 20 minutes to play!
        ## RUN 9 apr and it worked!!
        # self.N_network_size=300
        # self.N_network_size_practice=30
        # self.K_repeats_size=100
        # self.K_repeats_size_practice=10
        # self.M_length=10
        # self.bonus_payment = 2.00

        #run good on 12 apr morning: range limit about 10 min to play, shoerter network try to run apr 12 with v.0.6.0
        # self.N_network_size=200
        # self.N_network_size_practice=40
        # self.K_repeats_size=50
        # self.K_repeats_size_practice=15
        # self.M_length=5
        # self.bonus_payment = 1.0

        # self.range_min=15
        # self.range_max=85

        #some more minor changes. RUN APR 12
        # self.N_network_size=200
        # self.N_network_size_practice=40
        # self.K_repeats_size=70
        # self.K_repeats_size_practice=10
        # self.M_length=10
        # self.bonus_payment = 1.0

        #self.range_min=15
        #self.range_max=85

        self.N_network_size=20
        self.N_network_size_practice=20
        self.K_repeats_size=10
        self.K_repeats_size_practice=5
        self.M_length=5
        self.bonus_payment = 0.5
        self.range_min=15
        self.range_max=85



        self.Percent_attention_trials=200.0 #number of failed trials should be a bout 2x than the number of trials hence 200%
        self.Percent_failed_nodes= 90 #number of trials that can fail from all reasons (for example 95% means subject wasn't listening 95% of the time and this would fail all his data)
        #self.Percent_failed_nodes= 25 #changed it to 25% becuase almost always subject are very good and make very few mistakes -- I TRIED THIS IS IS DANGEROUS BECAUSE OTHER NODES IMIDIATELY START FAIL...
        self.UI_PROX_T= 11


        """ Wallace parameters """
        self.task = "The Line Game"
        self.verbose = False
        self.experiment_repeats = self.N_network_size  # N number of chains
        self.practice_repeats = self.N_network_size_practice    # N number of chains for practice
        self.K_all_trials=self.K_repeats_size+self.K_repeats_size_practice
        self.agent = LineAgent
        self.network = lambda: MultiChain(max_size=self.M_length)

        self.initial_recruitment_size = 10 # initital recuriemnt size (number of participants initally recruited) ##IMPORTANT THIS SHOULD BE more than 10 becuase if not you only have 10 subjects.
        self.instruction_pages = ["instructions/instruct-1.html",
                                  "instructions/instruct-2.html",
                                  "instructions/instruct-3.html",
                                  "instructions/instruct-4.html",
                                  "instructions/instruct-5.html"]
        self.debrief_pages = ["debriefing/debrief-1.html"]
        self.known_classes["LineInfo"] = LineInfo
        self.known_classes["LineSource"] = LineSource




        if not self.networks():
            self.setup()
        self.save()

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

        # if (K_repeats_size>len(possible_test_networks)):
        #     return None

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
        node.network.open = True


    def setup(self):
        super(LineGame, self).setup()
        for net in self.networks():
            if net.role == "practice":
                net.max_size = 500
            source = LineSource(network=net)
            source.create_pattern(self.range_min, self.range_max)
            source.generation = 0
            net.open = True

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

    def data_check(self, participant):
              # get the necessary data
        networks = Network.query.all()
        nodes = LineAgent.query.filter_by(participant_id=participant.id, failed=False).all()
        node_ids = [n.id for n in nodes]
        incoming_vectors = Vector.query.filter(Vector.destination_id.in_(node_ids)).all()
        outgoing_vectors = Vector.query.filter(Vector.origin_id.in_(node_ids)).all()

        try:
            # 1 source node per network
            for net in networks:
                sources = net.nodes(type=LineSource)
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
                infos =  node.infos(LineInfo)
                #print ([type(i) for i in  infos])
                ################### NORI #################
                ###original:
                ### assert (len([i for i in infos ]) == 1)

                if (len([i for i in infos ]) != 1):
                    node.fail()
                else:
                    info=infos[0]
                    ResponseRatio=info.contents
                    TrueRatio=info.true_seed
                    is_numeric = False
                    try:
                        ResponseRatio=int(info.contents)
                        is_numeric = True
                    except:
                        pass

                    if is_numeric:
                        assert (abs(ResponseRatio-TrueRatio)<=self.UI_PROX_T)
                    else:
                        assert (ResponseRatio=='NaN')

                    try:
                        assert len(node.transmissions(direction="all", status="pending")) == 0
                        assert len(node.transmissions(direction="incoming", status="received")) == 1
                    except:
                        print "Warning: had to fail nodes because of transmission error"
                        node.fail()

            self.log("Data check passed!")
            return True
        except:
            import traceback
            traceback.print_exc()
            return False


    def bonus(self, participant):
        tried_attempts=0
        good_trials=0
        overall_attempts=0;
        failed_nodes=0;
        not_good_trials=0;
        nodes = LineAgent.query.filter_by(participant_id=participant.id).all()
        for node in nodes:
            if node.failed:
                failed_nodes+=1
                tried_attempts+=1
            else:
#                infos = node.infos(type=LineInfo)
                infos = node.infos()
                for info in infos:
                    tried_attempts+=1
                    try:
                        num_attempts=int(info.property1)
                        #num_attempts=info.num_attempts
                    except:
                        num_attempts=0
                    if num_attempts==1:
                        good_trials+=1
                    if num_attempts>1:
                        not_good_trials+=1
        #self.log("\NORITHERE-len(nodes)= {} self.K_all_trials={} good_trials={}  failed_nodes={}".format(len(nodes),self.K_all_trials,good_trials,failed_nodes))
        score =  (0.2*len(nodes))/self.K_all_trials  + (0.8*good_trials)/self.K_all_trials #+ 0.2*(good_trials - failed_nodes ) * 1.0 / (tried_attempts)
        #score =  (1.0*good_trials)/self.K_all_trials
        score = score - 0.8*failed_nodes/self.K_all_trials - 0.5*not_good_trials/self.K_all_trials
        #score = round(score*100.0)/100.0
#        score = score*0.5 + 0.5
        #score = (good_trials - failed_nodes) * 1.0 / (tried_attempts)
        score = max (score, 0.02)
        score = min (score, 0.95)

        #if tried_attempts<5:
        #    score=0.10
        to_return_score=round(score*self.bonus_payment*100.0)/100.0
        return to_return_score

    # def attention_check(self, participant):
    #     bandits = Bandit.query.all()
    #     nodes = BanditAgent.query.filter_by(participant_id=participant.id).all()
    #     pulls = []
    #     for node in nodes:
    #         pulls.extend(node.infos(type=Pull))

    #     final_decisions = [p for p in pulls if p.check == "false"]
    #     checks = [p for p in pulls if p.check == "true"]

    #     times_found_treasure = 0
    #     times_chose_treasure = 0

    #     for d in final_decisions:
    #         if d.remembered == "false":
    #             right_answer = [b for b in bandits if b.network_id == d.network_id and b.bandit_id == d.bandit_id][0].good_arm
    #             checked_tiles = [int(c.contents) for c in checks if c.network_id == d.network_id and c.trial == d.trial]
    #             if right_answer in checked_tiles:
    #                 times_found_treasure += 1
    #                 if int(d.contents) == right_answer:
    #                     times_chose_treasure += 1

    #     diff = times_found_treasure - times_chose_treasure

    #     return diff < 300

    # NORIHERE:    The logic: #fail nodes / all nodes < Fail percent
    #                         $ property 1 (num of attempts) >1  / # trials < MoreHanOneAttemptPercent
########################### NORIHERE ################################

    def attention_check(self, participant):

        # how to retrieve failes nodes?
        tried_attempts=0
        tried_trials=0
        failed_nodes=0;
        nodes = LineAgent.query.filter_by(participant_id=participant.id).all()
        for node in nodes:
            if node.failed:
                failed_nodes+=1
            else:
                infos =  node.infos(type=LineInfo)
                for info in infos:
                     tried_attempts+=info.num_attempts
                     tried_trials+=1
        #print ("ATTENTION CHECK: failed_nodes:" + str(failed_nodes) + " tried_attempts: " + str(tried_attempts) + "tried_trials" + str(tried_trials))
        print "ATTENTION: tried_attempts: " + str(tried_attempts)
        print "ATTENTION: self.Percent_attention_trials: " + str(self.Percent_attention_trials)
        print "ATTENTION: tried_trials: " + str(tried_trials)

        if (tried_attempts*100>self.Percent_attention_trials*tried_trials):
            print "ATTENTION: failed attention test 1"
            return False
 #       failed_nodes=len(Node.query.filter_by(failed=True,participant_id=participant.id).all())
        print "ATTENTION: passed attention test 1"
        print "ATTENTION: failed_nodes: " + str(failed_nodes)
        print "ATTENTION: Percent_failed_nodes: " + str(self.Percent_failed_nodes)
        print "ATTENTION: len(nodes): " + str(len(nodes))

        #note that this should only apply when you have enought trials this is why tried_trials is suppose to be large (e.g >4)
        if ((100*failed_nodes>self.Percent_failed_nodes*len(nodes))):
            print "ATTENTION: failed attention test 2"
            return False
        print "ATTENTION: passed attention test (all)"
        return True
########################### NORIHERE ################################

########################### NORIHERE ################################
class LineInfo(Info):

#    __mapper_args__ = {"polymorphic_identity": "bandit_agent"}
    __mapper_args__ = {"polymorphic_identity": "line_info"}

    @hybrid_property
    def num_attempts(self):
        return int(self.property1)

    @num_attempts.setter
    def num_attempts(self, my_num_attempts):
        self.property1 = repr(my_num_attempts)

    @num_attempts.expression
    def num_attempts(self):
        return cast(self.property1, Integer)


    @hybrid_property
    def reaction_time(self):
        return float(self.property2)

    @reaction_time.setter
    def reaction_time(self, my_RT):
        self.property2 = repr(my_RT)

    @reaction_time.expression
    def reaction_time(self):
        return cast(self.property2, Float)


    @hybrid_property
    def true_seed(self):
        try:
            val=int(self.property3)
        except:
            val=self.property3
        return val

    @true_seed.setter
    def true_seed(self, my_true_seed):
        self.property3 = repr(my_true_seed)

    @true_seed.expression
    def true_seed(self):
        return cast(self.property3, Integer)

    @hybrid_property
    def result_list(self):
        return self.property4

    @result_list.setter
    def result_list(self, my_result_list):
        self.property4 = repr(my_result_list)

    @result_list.expression
    def result_list(self):
        return repr(self.property4)

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

class LineSource(Source):
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

    __mapper_args__ = {"polymorphic_identity": "line_source"}

    def _what(self):
        return LineInfo

    def create_pattern(self, range_min, range_max):
        #LineInfo(origin=self, contents=random.randint(0,100));
        LineInfo(origin=self, contents=random.randint(range_min,range_max));


class LineAgent(Agent):
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

        self.network.open= True #because the network might be stuck

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



    __mapper_args__ = {"polymorphic_identity": "line_agent"}

    def _what(self):
        return LineInfo




extra_routes = Blueprint(
    'extra_routes', __name__,
    template_folder='templates',
    static_folder='static')


# @extra_routes.route("/node/<int:node_id>/calculate_fitness", methods=["GET"])
# def calculate_fitness(node_id):

#     exp = BanditGame(db.session)
#     node = BanditAgent.query.get(node_id)
#     if node is None:
#         exp.log("Error: /node/{}/calculate_fitness, node {} does not exist".format(node_id))
#         page = exp.error_page(error_type="/node/calculate_fitness, node does not exist")
#         js = dumps({"status": "error", "html": page})
#         return Response(js, status=400, mimetype='application/json')

#     node.calculate_fitness()
#     exp.save()

#     data = {"status": "success"}
#     return Response(dumps(data), status=200, mimetype='application/json')


# @extra_routes.route("/num_trials", methods=["GET"])
# def get_num_trials():
#     exp = BanditGame(db.session)
#     data = {"status": "success",
#             "experiment_repeats": exp.experiment_repeats,
#             "practice_repeats": exp.practice_repeats,
#             "n_trials": exp.n_trials}
#     return Response(dumps(data), status=200, mimetype='application/json')


# @extra_routes.route("/num_bandits", methods=["GET"])
# def get_num_bandits():
#     exp = BanditGame(db.session)
#     data = {"status": "success", "num_bandits": exp.n_bandits}
#     return Response(dumps(data), status=200, mimetype='application/json')


# @extra_routes.route("/num_arms/<int:network_id>/<int:bandit_id>", methods=["GET"])
# def get_num_arms(network_id, bandit_id):
#     bandit = Bandit.query.filter_by(network_id=network_id, bandit_id=bandit_id).one()
#     data = {"status": "success", "num_arms": bandit.num_arms}
#     return Response(dumps(data), status=200, mimetype='application/json')


# @extra_routes.route("/good_arm/<int:network_id>/<int:bandit_id>", methods=["GET"])
# def good_arm(network_id, bandit_id):
#     bandit = Bandit.query.filter_by(network_id=network_id, bandit_id=bandit_id).one()
#     data = {"status": "success", "good_arm": bandit.good_arm}
#     return Response(dumps(data), status=200, mimetype='application/json')


# @extra_routes.route("/consent", methods=["GET"])
# def get_consent():
#     return return_page('consent.html', request)

@extra_routes.route("/is_practice/<int:network_id>", methods=["GET"])
def get_is_practice(network_id):
#    exp = LineGame(db.session)
    net=Network.query.get(network_id)
    data = {"status": "success", "is_practice": net.role == "practice"}
    return Response(dumps(data), status=200, mimetype='application/json')


@extra_routes.route("/trial_number_string/<int:node_id>/<int:participant_id>", methods=["GET"])
def get_trial_number_string(node_id,participant_id):
    exp = LineGame(db.session)
    node = LineAgent.query.get(node_id)
    participants = Participant.query.filter_by(id=participant_id).all()
    bonus=exp.bonus(participants[0])

    exp.log("/trial_number_string GET request. Params: node_id: {}."
            .format(node_id))

    # check the node exists for the current particiapnt
    nodes = len(LineAgent.query.filter_by(participant_id=node.participant_id).all())
    all_trials=exp.K_all_trials

    if node is None:
        exp.log("Error: /trial_number_string/{}, node {} does not exist".format(node_id, node_id))
        page = error_page(error_type="/trial_number_string, node does not exist")
        js = dumps({"status": "error", "html": page})
        return Response(js, status=400, mimetype='application/json')

    # return the data
    data = str(nodes) + " / " + str(all_trials) + ". Estimated bonus so far: " + str(bonus) + "$"
    data = {"status": "success", "trial_str": data, "generation": node.generation}
    exp.log("/trial_number_string GET request successful.")
    js = dumps(data, default=date_handler)
    return Response(js, status=200, mimetype='application/json')

# HERE!!!
# @extra_routes.route("/trial_number_string/<int:node_id>/<worker_id>", methods=["GET"])
# def get_status_all(node_id,worker_id):
#     exp = LineGame(db.session)
#     node = Agent.query.get(node_id)
#     participants = Participant.query.filter_by(workerid=worker_id).all()
#     bonus=exp.bonus(participants[0])

#     exp.log("/trial_number_string GET request. Params: node_id: {}."
#             .format(node_id))

 # print("Testing infos...", end="\r")
 #            sys.stdout.flush()

 #            for network in exp.networks():

 #                agents = network.nodes(type=Agent)
 #                source = network.nodes(type=Source)[0]

 #                assert len(source.infos()) == 1


 #            #     for bandit in bandits:
 #            #         assert len(bandit.infos()) == 0

 #                for agent in agents:
 #                    infos =  agent.infos()
 #                    assert len(infos) == 1
 #                    info=infos[0]
 #                    true_seed=info.true_seed
 #                    try:
 #                        contents=int(info.contents)
 #                    except:
 #                        assert (contents=='NaN')
 #                    else:
 #                        assert (abs(contents-true_seed)<exp.UI_PROX_T)




# @extra_routes.route("/instructions/<int:page>", methods=["GET"])
# def get_instructions(page):
#     exp = LineGame(db.session)
#     return return_page(exp.instruction_pages[page-1], request)


# @extra_routes.route("/debrief/<int:page>", methods=["GET"])
# def get_debrief(page):
#     exp = LineGame(db.session)
#     return return_page(exp.debrief_pages[page-1], request)


# @extra_routes.route("/stage", methods=["GET"])
# def get_stage():
#     return return_page('stage.html', request)



# @extra_routes.route("/participant/<worker_id>/<hit_id>/<assignment_id>", methods=["POST"])
# def create_participant(worker_id, hit_id, assignment_id):
#     exp = LineGame(db.session)

#     parts = Participant.query.filter_by(workerid=worker_id).all()
#     if parts:
#         print "participant already exists!"
#         return Response(status=200)

#     p = Participant(workerid=worker_id, assignmentid=assignment_id, hitid=hit_id)
#     exp.save(p)
#     return Response(status=200)


#@extra_routes.route("/dashboard/<int:number_of_participants_to_check>/<int:number_of_current_participants>", methods=["GET"])
#def dashboard(number_of_participants_to_check,number_of_current_participants):
@extra_routes.route("/dashboard", methods=["GET"])
def dashboard():
    number_of_participants_to_check = 0 # Everybody!
    number_of_current_participants = 10  #highlight the last 10 participant
    try:
        exp = LineGame(db.session) #ge the experiment's basics
        networks = exp.networks()
        participants = Participant.query.all()
        print("participants:")
        print participants

      # find the last participants that played
        dates={p.creation_time:p for p in participants}
        sorted_dates_tuples=sorted(dates.items())
        # check that number_of_participants_to_check
        if number_of_participants_to_check==0:
            number_of_participants_to_check= len(sorted_dates_tuples)
        my_num_parts= min ([number_of_participants_to_check, len(sorted_dates_tuples) ])
        if number_of_current_participants==0:
            number_of_current_participants=1;
        number_of_current_participants=min([number_of_current_participants,my_num_parts])

        selected_participants_ids=[k[1].id for k in sorted_dates_tuples[(-my_num_parts):]] #this the partcipants that we are going to look for
        current_participants_ids=[k[1].id for k in sorted_dates_tuples[(-number_of_current_participants):]] #these are the very last participants

        #print("select participants:")
        #print selected_participants_ids
        #print("current_participants_ids:")
        #print current_participants_ids

        chain_dic = dict([(n.id,n.size(type=LineAgent)) for n in networks])
        chain_list= [ chain_dic[k] for k in chain_dic.keys()]

        chain_dic_role = dict([(n.id,n.role) for n in networks])
        chain_list_role = [ chain_dic_role[k] for k in chain_dic_role.keys()]
        chain_list_role_s = ["e" if r=="experiment" else "p" for r in chain_list_role]

        chain_dic_failed = dict([(n.id,n.size(type=None, failed=True)) for n in networks])
        chain_list_failed= [ chain_dic_failed[k] for k in chain_dic_failed.keys()]

        dates={p.creation_time:p for p in participants}
        sorted_dates_tuples=sorted(dates.items())
        selected_participants_bonus=sum([k[1].bonus for k in sorted_dates_tuples[(-my_num_parts):] if k[1].bonus is not None])
        all_participants_bonus=sum([k[1].bonus for k in sorted_dates_tuples if k[1].bonus is not None])

        all_chain_length=sum(chain_list)
        min_chain_length=min(chain_list)
        max_chain_length=max(chain_list)
        num_failed_nodes=len(Node.query.filter_by(failed=True).all())
        selected_participants_num=len(selected_participants_ids)

        summary={"all_bonus": all_participants_bonus, "selected_part_num": selected_participants_num, "selected_part_bonus": selected_participants_bonus, "all_chain_length": all_chain_length, "max_chain_length":max_chain_length, "min_chain_length": min_chain_length, "num_failed_nodes": num_failed_nodes, "all_chain_lengths": str(chain_list), "all_chain_lengths_failed": str(chain_list_failed), "chain_list_role_s": chain_list_role_s}

        summary_node_dict={} # create empty dict for all chains that selected participant paticipated with
        summary_node_dict_fail=dict([(p,{}) for p in selected_participants_ids]) #create an empty dict for all failed participants

        #deal with the non failed nodes first!
        for network in networks:
            agents = network.nodes(type=LineAgent)
            relevant_agents = [agent for agent in agents if agent.participant_id in selected_participants_ids]
            if not(relevant_agents): # if this network do not touch the list of particiapnts
                continue
            summary_node_dict[network.id]={}
            summary_node_dict[network.id]['label']=network.id
            summary_node_dict[network.id]['role']=network.role
            summary_node_dict[network.id]['current']=False
            if network.role == "experiment":
                summary_node_dict[network.id]['x']=[-1] * (exp.M_length + 2)
                summary_node_dict[network.id]['y']=[-1] * (exp.M_length + 2)
            else:
                summary_node_dict[network.id]['x']=[-1] * (max_chain_length + 2)
                summary_node_dict[network.id]['y']=[-1] * (max_chain_length + 2)
            for agent in agents:
                agent_p_id=agent.participant_id
                if agent_p_id in current_participants_ids:
                    summary_node_dict[network.id]['label']=str(network.id) + "|" + str(agent_p_id)
                    summary_node_dict[network.id]['current']=True
                infos =  agent.infos()
                for info in infos:
                    is_fail=info.failed
                    generation=info.generation
                    true_seed=info.true_seed

                    try:
                        contents=int(info.contents)
                    except:
                        contents=None

                    net_role=network.role
                    net_id=network.id
                    part_id=agent.participant_id
                    target=contents
                    value_source=true_seed

                    summary_node={"net_role": net_role, "net_id": net_id, "is_fail": is_fail, "target": target, "source": value_source}
                    str_summary="net_role: {} net_id: {} is_fail: {} part_id: {} target: {} source: {}".format(net_role,net_id,is_fail,part_id,target,value_source)
                    #print("is_fail:"+ str(is_fail) + " contents:" + str(contents) )
                    if not(is_fail):
                        gen = generation
                        if (generation<len(summary_node_dict[network.id]['x'])) and (target>=0) and (target<=100):
                            summary_node_dict[network.id]['x'][generation]=gen
                            summary_node_dict[network.id]['y'][generation]=target

                        if generation==1:
                           gen = 0
                           summary_node_dict[network.id]['x'][0]=gen
                           summary_node_dict[network.id]['y'][0]=value_source

        for network in networks:
            agents = Node.query.filter_by(failed=True , network_id=network.id).all()
            #print("network.id")
            #print(network.id)
            #print("agents (failed):")
            #print(agents)
            #print("selected paticipants:")
            #print(selected_participants_ids)
            #print("->-.-----")
            for agent in agents:
                agent_p_id=agent.participant_id
                #print("->-.-----******")
                #print agent_p_id
                #print(selected_participants_ids)
                if agent_p_id in selected_participants_ids:
                    if not(summary_node_dict_fail[agent_p_id]):
                        summary_node_dict_fail[agent_p_id]['label']=agent_p_id
                        summary_node_dict_fail[agent_p_id]['current']=False
                        summary_node_dict_fail[agent_p_id]['x']=[]
                        summary_node_dict_fail[agent_p_id]['y']=[]
                        summary_node_dict_fail[agent_p_id]['role']=[]

                    generation = agent.generation
                    #infos =  agent.infos()
                    true_seed=0
                    infos =  Info.query.filter_by(origin_id=agent.id, failed=True)
                    for info in infos:
                        true_seed = info.true_seed
                    gen = generation-1;
                    #print("*****")
                    #print(agent)
                    #print("gen:"+ str(generation) + " true_seed:" + str(true_seed) + "failed:" + str(agent.failed))
                    # if network.role=="experiment":
                    #     assert(generation<=(exp.M_length+1))
                    summary_node_dict_fail[agent_p_id]['x'].append(gen)
                    summary_node_dict_fail[agent_p_id]['y'].append(true_seed)
                    summary_node_dict_fail[agent_p_id]['role'].append("e" if network.role=="experiment" else "p")
                    #print('summary_node_dict_fail at initialization')
                        #print (summary_node_dict_fail)

                if agent_p_id in current_participants_ids:
                    summary_node_dict_fail[agent_p_id]['label']=str(agent_p_id)+ "<" + str(network.id)
                    summary_node_dict_fail[agent_p_id]['current']=True

        sps="      *****************           "
        #print('****> summary_node_dict final')
        #print (dumps(summary_node_dict))
        #print('****> summary_node_dict_fail final')
        #print (dumps(summary_node_dict_fail))
        # return Response(
        #         dumps(summary) + sps + dumps(summary_node_dict) + sps + dumps(summary_node_dict_fail) ,
        #         status=200,
        #         mimetype='application/json')
        return render_template('dashboard.html', summary=dumps(summary), chains=dumps(summary_node_dict), failure_points=dumps(summary_node_dict_fail))
        # mjson= {{ summary }}
        # cjson= {{ chains }}
        # fjson= {{ failure_points}}
    except Exception:
        import traceback
        return Response(dumps(traceback.print_exc()), status=400)


# @extra_routes.route("/ad_address/<mode>/<hit_id>", methods=["GET"])
# def ad_address(mode, hit_id):

#     if mode == "debug":
#         address = '/complete'
#     elif mode in ["sandbox", "live"]:
#         CONFIG = PsiturkConfig()
#         CONFIG.load_config()
#         username = os.getenv('psiturk_access_key_id', CONFIG.get("psiTurk Access", "psiturk_access_key_id"))
#         password = os.getenv('psiturk_secret_access_id', CONFIG.get("psiTurk Access", "psiturk_secret_access_id"))
#         try:
#             req = requests.get('https://api.psiturk.org/api/ad/lookup/' + hit_id,
#                                auth=(username, password))
#         except:
#             raise ValueError('api_server_not_reachable')
#         else:
#             if req.status_code == 200:
#                 hit_address = req.json()['ad_id']
#             else:
#                 raise ValueError("something here")
#         if mode == "sandbox":
#             address = 'https://sandbox.ad.psiturk.org/complete/' + str(hit_address)
#         elif mode == "live":
#             address = 'https://ad.psiturk.org/complete/' + str(hit_address)
#     else:
#         raise ValueError("Unknown mode: {}".format(mode))
#     return Response(dumps({"address": address}), status=200)


# def return_page(page, request):
#     exp = LineGame(db.session)
#     try:
#         hit_id = request.args['hit_id']
#         assignment_id = request.args['assignment_id']
#         worker_id = request.args['worker_id']
#         mode = request.args['mode']
#         return render_template(
#             page,
#             hit_id=hit_id,
#             assignment_id=assignment_id,
#             worker_id=worker_id,
#             mode=mode
#         )
#     except:
#         return exp.error_page(error_type="{} AWS args missing".format(page))


# def request_parameter(request, parameter, parameter_type=None, default=None):
#     """ Get a parameter from a request

#     The request object itself must be passed.
#     parameter is the name of the parameter you are looking for
#     parameter_type is the type the parameter should have
#     default is the value the parameter takes if it has not been passed

#     If the parameter is not found and no default is specified,
#     or if the parameter is found but is of the wrong type
#     then a Response object is returned"""

#     exp = LineGame(db.session)

#     # get the parameter
#     try:
#         value = request.values[parameter]
#     except KeyError:
#         # if it isnt found use the default, or return an error Response
#         if default is not None:
#             return default
#         else:
#             msg = "{} {} request, {} not specified".format(request.url, request.method, parameter)
#             exp.log("Error: {}".format(msg))
#             data = {
#                 "status": "error",
#                 "html": error_page(error_type=msg)
#             }
#             return Response(
#                 dumps(data),
#                 status=400,
#                 mimetype='application/json')

#     # check the parameter type
#     if parameter_type is None:
#         # if no parameter_type is required, return the parameter as is
#         return value
#     elif parameter_type == int:
#         # if int is required, convert to an int
#         try:
#             value = int(value)
#             return value
#         except ValueError:
#             msg = "{} {} request, non-numeric {}: {}".format(request.url, request.method, parameter, value)
#             exp.log("Error: {}".format(msg))
#             data = {
#                 "status": "error",
#                 "html": error_page(error_type=msg)
#             }
#             return Response(
#                 dumps(data),
#                 status=400,
#                 mimetype='application/json')
#     elif parameter_type == "known_class":
#         # if its a known class check against the known classes
#         try:
#             value = exp.known_classes[value]
#             return value
#         except KeyError:
#             msg = "{} {} request, unknown_class: {} for parameter {}".format(request.url, request.method, value, parameter)
#             exp.log("Error: {}".format(msg))
#             data = {
#                 "status": "error",
#                 "html": error_page(error_type=msg)
#             }
#             return Response(
#                 dumps(data),
#                 status=400,
#                 mimetype='application/json')
#     elif parameter_type == bool:
#         # if its a boolean, convert to a boolean
#         if value in ["True", "False"]:
#             return value == "True"
#         else:
#             msg = "{} {} request, non-boolean {}: {}".format(request.url, request.method, parameter, value)
#             exp.log("Error: {}".format(msg))
#             data = {
#                 "status": "error",
#                 "html": error_page(error_type=msg)
#             }
#             return Response(
#                 dumps(data),
#                 status=400,
#                 mimetype='application/json')
#     else:
#         msg = "/{} {} request, unknown parameter type: {} for parameter {}".format(request.url, request.method, parameter_type, parameter)
#         exp.log("Error: {}".format(msg))
#         data = {
#             "status": "error",
#             "html": error_page(error_type=msg)
#         }
#         return Response(
#             dumps(data),
#             status=400,
#             mimetype='application/json')


# def error_page(participant=None, error_text=None, compensate=True,
#                error_type="default"):
#     """Render HTML for error page."""
#     if error_text is None:

#         error_text = """There has been an error and so you are unable to
#         continue, sorry! If possible, please return the assignment so someone
#         else can work on it."""

#         if compensate:
#             error_text += """Please use the information below to contact us
#             about compensation"""

#     if participant is not None:
#         hit_id = participant.hitid,
#         assignment_id = participant.assignmentid,
#         worker_id = participant.workerid
#     else:
#         hit_id = 'unknown'
#         assignment_id = 'unknown'
#         worker_id = 'unknown'

#     return render_template(
#         'error_wallace.html',
#         error_text=error_text,
#         compensate=compensate,
#         contact_address=config.get(
#             'HIT Configuration', 'contact_email_on_error'),
#         error_type=error_type,
#         hit_id=hit_id,
#         assignment_id=assignment_id,
#         worker_id=worker_id
#     )


def date_handler(obj):
    """Serialize dates."""
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj
