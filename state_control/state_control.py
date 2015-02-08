# NOTE THIS HAS NOT BEEN RUN! 

import threading
from threading import Timer
import time
import json
import random
import sys
import cPickle as pickle
from state_codes import *

if sys.platform == 'win32': #windoze
    import pyHook #for universal keyboard input
    import pythoncom

class ChangeYourBrainStateControl( object ):

    def __init__(self,client_name, sb_server, ecg, vis_period_sec = .25, baseline_sec = 30, condition_sec = 90, baseline_inst_sec = 10, condition_inst_sec = 20):
        self.client_name = client_name
        self.sb_server = sb_server
        self.ecg = ecg
        self.set_state(NO_EXPERIMENT)
        self.condition_state = NO_CONDITION
        self.tag_time = 0 #last time someone tagged in
        self.vis_period = vis_period_sec
        self.baseline_seconds = baseline_sec
        self.condition_seconds = condition_sec
        self.baseline_instruction_seconds = baseline_inst_sec 
        self.condition_instruction_seconds = condition_inst_sec

        #keyboard input (or fake if not windows)
        if sys.platform == 'win32': #windoze
            self.kInputThread = WindowsKeyboardInput(self)
            self.kInputThread.daemon = True;
            self.kInputThread.start()
        else:
            self.kInputThread = FakeKeyboardInput(self)
            self.kInputThread.daemon = True;
            self.kInputThread.start()
        # self.kInputThread = ConsoleKeyboardInputThread()
        # self.kInputThread.start()

        self.alpha_buffer = [] #buffering eeg alpha freq
        self.poll_answer = False #temp holding of subjective rating
        self.ecg_leadon = False #start with lead off as current state
        self.filename_prepend = "exploratorium_cyb"

    ### CALLED VIA SPACEBREW CLIENT LISTENER ############
    def process_eeg_alpha(self,value):
        arrValue = value.split(',')
        self.alpha_buffer.append(arrValue)
        # print('process_eeg_alpha called')
        ### make sure buffer gets clear when no subjects
        ### log data

    def tag_in(self,muse_id='0000'):
        #devNote: put here possible confirmation of user change if in middle of experiment
        self.tag_time = time.time()
        print 'tagged in at',self.tag_time
        self.alpha_save_condition = {'time': [], 'value':[], 'all': []}
        self.hrv_save_condition = {'time': [], 'value': [], 'device_time': []}

        self.alpha_save_baseline = {'time': [], 'value':[], 'all': []}
        self.hrv_save_baseline = {'time': [], 'value':[], 'device_time': []}

        self.meta_data = {'time': [time.time(),], 'value':['TAG_IN',]} #program state etc

        self.start_setup_instructions()

    ######################################################
    ### STATE CHANGING ############
    def set_state(self,state):
        self.experiment_state = state
        print time.time(),state

    def start_setup_instructions(self):
        #devNote: possibly add both time-in and time-out timer here which takes us back to (no experiment)
        self.set_state(SETUP_INSTRUCTIONS)        
        self.output_instruction()
        self.do_every_while(self.vis_period,SETUP_INSTRUCTIONS,self.start_on_lead) #start as soon as we see ECG lead on

    def start_baseline_instructions(self):
        if self.experiment_state not in [SETUP_INSTRUCTIONS,BASELINE_CONFIRMATION]:
            return
        self.set_state(BASELINE_INSTRUCTIONS)
        self.output_instruction()
        instruction_timer = Timer(self.baseline_instruction_seconds,self.start_baseline_collection) 
        instruction_timer.start()
        
    def start_baseline_collection(self):
        if self.experiment_state != BASELINE_INSTRUCTIONS:
            return        
        self.set_state(BASELINE_COLLECTION)
        self.meta_data['value'].append(('state','BASELINE_COLLECTION'))
        self.meta_data['time'].append(time.time())

        #tell viz to go to the baseline screen 
        instruction = {"message": {
             "value" : {'instruction_name': 'BASELINE_COLLECTION', 'display_seconds': self.baseline_seconds},
             "type": "string", "name": "instruction", "clientName": self.client_name}}    
        self.sb_server.ws.send(json.dumps(instruction))
        print "start baseline collection" 

        baseline_timer = Timer(self.baseline_seconds,self.start_post_baseline)
        baseline_timer.start()
        self.do_every_while(self.vis_period,BASELINE_COLLECTION,self.output_baseline) # instruct vis to start plotting 

    def start_post_baseline(self):
        """ask for confirmation + subjective feedback + selection of condition"""
        if self.experiment_state != BASELINE_COLLECTION:
            return
        self.set_state(BASELINE_CONFIRMATION)
        # self.baseline_confirmation = 1 ###TEMP!
        self.baseline_confirmation = 0 #confirmed = 1, disconfirmed = -1
        self.output_instruction('CONFIRMATION')
        while not self.baseline_confirmation: #neither confirmed nor disconfirmed
            self.check_ecg_lead() #should turn on ECG cconnection 
            continue
        if self.baseline_confirmation < 0: 
            self.start_baseline_instructions()
            print 'returning from post_baseline after disconfirmation of correct collection'
            return
        ### collect subj info
        self.baseline_subj = []
        for question in ['Q1','Q2','Q3','Q4']:
            self.output_instruction(question)
            while not self.poll_answer:
            self.check_ecg_lead() #should turn on ECG cconnection 
                if self.experiment_state != BASELINE_CONFIRMATION: #ensure we are in right state
                    return
                continue
            print self.baseline_subj
            self.baseline_subj.append(self.poll_answer)
            self.poll_answer = False

        print 'baseline user answers: ',self.baseline_subj
        self.start_condition_instructions()

    def start_condition_instructions(self):
        if self.experiment_state not in [BASELINE_CONFIRMATION,CONDITION_CONFIRMATION]:
            return
        ### differentiate between the three possible conditions (currently assuming breathing)
        self.set_state(CONDITION_INSTRUCTIONS)
        self.output_instruction()
        instruction_timer = Timer(self.condition_instruction_seconds,self.start_condition_collection) 
        instruction_timer.start()

    def start_condition_collection(self):
        if self.experiment_state != CONDITION_INSTRUCTIONS: 
            return
        self.set_state(CONDITION_COLLECTION)
        self.meta_data['value'].append(('state',CONDITION_COLLECTION))
        self.meta_data['time'].append(time.time())

        ### make sure to change this to average from start of baseline collection
        if self.alpha_save_baseline['value']:
            self.baseline_alpha = sum(self.alpha_save_baseline['value']) / len(self.alpha_save_baseline['value'])
        else:
            self.baseline_alpha = 0 ### change me to something better
        if self.hrv_save_baseline['value']:
            self.baseline_hrv = self.hrv_save_baseline['value'][-1]
        else:
            self.baseline_hrv = 0 ### change me

        #tell viz to go to the condition screen 
        instruction = {"message": {
             "value" : {'instruction_name': 'CONDITION_COLLECTION',
                         'display_seconds': self.condition_seconds,
                         'baseline_alpha' : self.baseline_alpha,
                         'baseline_hrv' : self.baseline_hrv},
             "type": "string", "name": "instruction", "clientName": self.client_name}}    
        self.sb_server.ws.send(json.dumps(instruction))
        print "start condition collection" #^^^
        print 'display_seconds:', self.condition_seconds
        print 'baseline_alpha',self.baseline_alpha
        print 'baseline_hrv', self.baseline_hrv

        condition_timer = Timer(self.condition_seconds,self.start_post_condition) 
        condition_timer.start()
        ### ??? send instructor
        self.do_every_while(self.vis_period,CONDITION_COLLECTION,self.output_condition) # instruct vis to start plotting 

    def start_post_condition(self):
        """ask for confirmation + subjective feedback"""
        if self.experiment_state != CONDITION_COLLECTION: 
            return
        self.set_state(CONDITION_CONFIRMATION)
        # self.condition_confirmation = 1 #TEMP
        self.condition_confirmation = 0 #confirmed = 1, disconfirmed = -1
        self.output_instruction('CONFIRMATION')
        while not self.condition_confirmation: #neither confirmed nor disconfirmed
            self.check_ecg_lead() #should turn on ECG cconnection 
            continue
        if self.condition_confirmation < 0: 
            self.start_condition_instructions()
            print 'returning from post_condition'
            return
        self.condition_subj = []
        #collect subj info
        for question in ['Q1','Q2','Q3','Q4']:
            self.output_instruction(question)
            while not self.poll_answer:
                self.check_ecg_lead() #should turn on ECG cconnection 
                if self.experiment_state != CONDITION_CONFIRMATION: #ensure we are in right state
                    return
                continue
            self.condition_subj.append(self.poll_answer)
            self.poll_answer = False

        print 'condition user answers: ',self.condition_subj
        self.start_post_experiment()

    def start_post_experiment(self):
        """display aggregates and wait for new tag in!"""
        if self.experiment_state != CONDITION_CONFIRMATION: 
            return
        self.set_state(POST_EXPERIMENT)
        self.output_post_experiment()

    ######################################################
    ### OUTPUT TO VISUALIZTION ###########################

    def output_instruction(self,sub_state=None):
        if self.experiment_state == SETUP_INSTRUCTIONS:
            instruction_text = 'This booth requires approximately a three minute commitment. To begin, sit down, put on headphones, and place hands on sensors.'
        elif self.experiment_state == BASELINE_INSTRUCTIONS:
            instruction_text = 'Give us 30 seconds to calibrate to your brain and body. Please stay still and silent, keeping your hands on the sensors.'
        elif self.experiment_state == CONDITION_INSTRUCTIONS:
            instruction_text = 'In this practice, you will slow your breath to one breath every 8 seconds. Return your hands to the sensors and follow the inhalation/exhalation visual as closely as possible. As the circle expands, breathe in. As it shrinks breathe out.'
        elif self.experiment_state in [CONDITION_CONFIRMATION,BASELINE_CONFIRMATION]:
            if sub_state == "CONFIRMATION" and self.experiment_state == BASELINE_CONFIRMATION:
                instruction_text = "Did you stay still and silent successfully during the calibration? You may remove your left hand from the sensor and type \'1\' for yes and \'0\' for no."
            elif sub_state == "CONFIRMATION" and self.experiment_state == CONDITION_CONFIRMATION:
                instruction_text = "Did you complete the exercise correctly? You may remove your left hand from the sensor and type \'1\' for yes and \'0\' for no."
            elif sub_state == "Q1":
                instruction_text = "How calm do you feel? Type a number between 1 (not at all) and 9 (very)"
            elif sub_state == "Q2":
                instruction_text = 'How content are you? (1-9)'
            elif sub_state == "Q3":
                instruction_text = 'How distracted are you? (1-9)' 
            elif sub_state == "Q4":
                instruction_text = 'How joyous do you feel? (1-9)' 
            else:
                raise Exception ('Unkown sub_state for instruction sent in state ' + str(self.experiment_state))
        else:
            raise Exception ('Unkown state ({}) for instruction sent'.format(self.experiment_state))
        print "output instruction: {}".format(instruction_text) 
        instruction = {"message": {
            "value" : {'instruction_name': 'DISPLAY_INSTRUCTION', 'instruction_text': instruction_text},
            "type": "string", "name": "instruction", "clientName": self.client_name}}    
        self.sb_server.ws.send(json.dumps(instruction))
        self.meta_data['value'].append(('state',self.experiment_state))
        self.meta_data['time'].append(time.time())

    def output_baseline(self):
        """output aggregated EEG and HRV values"""
        #devNote: possibly switch to outputting raw ECG (or heart rate!) instead of HRV during baseline
        if self.alpha_buffer:
            alpha_out = (float(self.alpha_buffer[-1][1])+float(self.alpha_buffer[-1][2]))/2 ### should modify this to average across TIME!            
            self.alpha_save_baseline['time'].append(time.time())
            self.alpha_save_baseline['value'].append(alpha_out)
            self.alpha_save_baseline['all'].append(self.alpha_buffer[-1]) #for saving. format: 4 sensor vals + device time (s) + d time(micros)
        else: 
            alpha_out = 0 # random.random() ###
            print 'baseline: alpha_buffer empty!'
        self.alpha_buffer = []

        # print "hrv type:",type(self.ecg.get_hrv())
        # print "hrv:",self.ecg.get_hrv()
        self.hrv_save_baseline['time'].append(time.time())
        self.hrv_save_baseline['value'].append(self.ecg.get_hrv())
        self.hrv_save_baseline['device_time'].append(self.ecg.get_hrv_t())
        value_out = "{:.1f},{:.2f},{:.2f}".format(time.time()-self.tag_time,alpha_out,self.ecg.get_hrv())
        message = {"message": { #send synced EEG & ECG data here
             "value": value_out,
             "type": "string", "name": "eeg_ecg", "clientName": self.client_name}}
        self.sb_server.ws.send(json.dumps(message))
        # print "output baseline: {}".format(value_out) #^^^

    def output_condition(self):
        """output aggregated EEG and HRV values"""
        # note: currently the same as output_baseline
        if self.alpha_buffer:
            alpha_out = (float(self.alpha_buffer[-1][1])+float(self.alpha_buffer[-1][2]))/2 ### change this to avg across whole thing
            self.alpha_save_condition['time'].append(time.time())
            self.alpha_save_condition['value'].append(alpha_out)
            self.alpha_save_condition['all'].append(self.alpha_buffer[-1]) #for saving. format: 4 sensor vals + time (s) + time(micros)
        else: 
            alpha_out = 0 #random.random()
        self.alpha_buffer = []

        self.hrv_save_condition['time'].append(time.time())
        self.hrv_save_condition['value'].append(self.ecg.get_hrv())
        self.hrv_save_condition['device_time'].append(self.ecg.get_hrv_t())

        value_out = "{:.1f},{:.2f},{:.2f}".format(time.time()-self.tag_time,alpha_out,self.ecg.get_hrv())
        message = {"message": { #send synced EEG & ECG data here
             "value": value_out,
             "type": "string", "name": "eeg_ecg", "clientName": self.client_name}}
        self.sb_server.ws.send(json.dumps(message))
        # print "output condition: {}".format(value_out) #^^^

    def output_post_experiment(self):

        if len(self.alpha_save_condition['value']):
            condition_alpha = sum(self.alpha_save_condition['value'])/len(self.alpha_save_condition['value'])
        else:
            condition_alpha = 0

        if self.hrv_save_condition['value']:
            condition_hrv = self.hrv_save_condition['value'][-1]
        else:
            condition_hrv = 0 ### change me
            print 'no hrv collected for condition!'

        #output to vis
        value_out = {"instruction_name":"POST_EXPERIMENT",
                    "baseline_hrv": self.baseline_hrv,
                    "baseline_alpha": self.baseline_alpha,
                    "baseline_subj": self.baseline_subj,
                    "condition_hrv": condition_hrv,
                    "condition_alpha": condition_alpha,
                    "condition_subj": self.condition_subj}
        message = {"message": { 
             "value": value_out,
             "type": "string", "name": "instruction", "clientName": self.client_name}}
        self.sb_server.ws.send(json.dumps(message))

        #save data to file
        (tm_year,tm_mon,tm_mday,tm_hour,tm_min,tm_sec,tm_wday,tm_yday,tm_isdst) = time.localtime() #get local time
        filename = '%s_%d.%02d.%02d_%d.%d.%d.dat' % (self.filename_prepend,tm_year,tm_mon,tm_mday,tm_hour,tm_min,tm_sec) 
        output_dict = {
            'metadata': self.meta_data,
            'hrv baseline': self.hrv_save_baseline,
            'hrv condition': self.hrv_save_condition,
            'hrv baseline': self.hrv_save_baseline,
            'hrv condition': self.hrv_save_condition,
        }
        pickle.dump( output_dict, open( filename, "wb" ) )

        print "output post experiment",value_out 

    ######################################################
    ### HELPER ###########################################

    def do_every_while(self,period,state,f,*args):
        """Run function f() every period seconds while experiment_state == state."""
        def g_tick():
            t = time.time()
            count = 0
            while True:
                count += 1
                yield t + count*period - time.time()
        g = g_tick()
        while self.experiment_state == state:
            self.check_ecg_lead() #should turn on ECG cconnection 
            time.sleep(g.next())
            self.check_ecg_lead() #check the ECG lead here
            f(*args)

    def start_on_lead(self):
        if self.ecg.is_lead_on():
            self.check_ecg_lead() #should turn on ECG cconnection 
            self.start_baseline_instructions() # and then start the state engine

    def check_ecg_lead(self):
        """ check to see the current state of the ECG lead, and send a message if it changes """
        if self.ecg.cur_lead_on != self.ecg_leadon: 
            self.ecg_leadon = self.ecg.cur_lead_on
            if self.ecg_leadon:
                instruction = {"message": {
                    "value" : {'instruction_name': 'CONNECTED', 'type': 'ecg'},
                    "type": "string", "name": "instruction", "clientName": self.client_name}}
                print "ECG CONNECTED" #^^^
            else:    
                instruction = {"message": {
                    "value" : {'instruction_name': 'DISCONNECTED', 'type': 'ecg'},
                    "type": "string", "name": "instruction", "clientName": self.client_name}}
                print "ECG DISCONNECTED" #^^^
            self.sb_server.ws.send(json.dumps(instruction))
            self.meta_data['time'].append(time.time())
            self.meta_data['value'].append(('ecg_leadon',self.ecg_leadon)) #record this in metadata

    def keyboard_input(self):
        #devNote: could do this smarter by not calling this function unless in one of the appropriate states
        if self.experiment_state == SETUP_CONFIRMATION:
            input = ''
            while input != '1':
                print 'When you are set up and seated, type \'1\' and press enter'
                input = raw_input()
            ### select condition
            self.start_baseline_instructions()
        elif self.experiment_state == BASELINE_CONFIRMATION:
            pass
            ### confirm valid trial, collect subjective info and proceed to condition
        elif self.experiment_state == CONDITION_CONFIRMATION:
            pass
            ### confirm valid trial, collect subjective info and proceed to final display %%%
        #(otherwise do nothing!)

    def win_keyboard_input(self,key_ID):
        #note: each key has 2 IDs because of Num Lock
        if self.experiment_state == BASELINE_CONFIRMATION:
            if not self.baseline_confirmation:
                if key_ID in [96,45]: #zero
                    print 'baseline disconfirmed'
                    self.baseline_confirmation = -1
                elif key_ID in [97,35]: #one
                    print 'baseline confirmed'
                    self.baseline_confirmation = 1
            elif not self.poll_answer:
                if key_ID in [97,35]: 
                    self.poll_answer = 1
                elif key_ID in [98,40]: 
                    self.poll_answer = 2
                elif key_ID in [99,34]: 
                    self.poll_answer = 3
                elif key_ID in [100,37]: 
                    self.poll_answer = 4
                elif key_ID in [101,12]: 
                    self.poll_answer = 5
                elif key_ID in [102,39]: 
                    self.poll_answer = 6
                elif key_ID in [103,36]: 
                    self.poll_answer = 7
                elif key_ID in [104,38]: 
                    self.poll_answer = 8
                elif key_ID in [105,33]: 
                    self.poll_answer = 9
        elif self.experiment_state == CONDITION_CONFIRMATION:
            if not self.condition_confirmation:
                if key_ID in [96,45]: #zero
                    print 'condition disconfirmed'
                    self.condition_confirmation = -1
                elif key_ID in [97,35]: #one
                    print 'condition confirmed'
                    self.condition_confirmation = 1
            elif not self.poll_answer:
                if key_ID in [97,35]: 
                    self.poll_answer = 1
                elif key_ID in [98,40]: 
                    self.poll_answer = 2
                elif key_ID in [99,34]: 
                    self.poll_answer = 3
                elif key_ID in [100,37]: 
                    self.poll_answer = 4
                elif key_ID in [101,12]: 
                    self.poll_answer = 5
                elif key_ID in [102,39]: 
                    self.poll_answer = 6
                elif key_ID in [103,36]: 
                    self.poll_answer = 7
                elif key_ID in [104,38]: 
                    self.poll_answer = 8
                elif key_ID in [105,33]: 
                    self.poll_answer = 9
        #(otherwise do nothing!)

class ConsoleKeyboardInputThread ( threading.Thread ):
    
    def __init__(self):
        super(ConsoleKeyboardInputThread, self).__init__()
        self.running = True

    def stop ( self ):
        self.running = False

    def run ( self ):
        while self.running:
            keyboard_input()


class WindowsKeyboardInput ( threading.Thread ):
    
    def __init__(self, sc_instance):
        super(WindowsKeyboardInput, self).__init__()
        self.state_control = sc_instance

    def stop ( self ):
        pass

    def run ( self ):
        # create a hook manager
        hm = pyHook.HookManager()
        # watch for all mouse events
        hm.KeyDown = self.OnKeyboardEvent
        # set the hook
        hm.HookKeyboard()
        # wait forever
        pythoncom.PumpMessages()

    def OnKeyboardEvent(self,event):
        #print 'Key:', event.Key
        print 'KeyID:', event.KeyID
        self.state_control.win_keyboard_input(event.KeyID)

        # return True to pass the event to other handlers
        return True


class FakeKeyboardInput ( threading.Thread ):
    
    def __init__(self, sc_instance):
        super(FakeKeyboardInput, self).__init__()
        self.state_control = sc_instance

    def stop ( self ):
        pass

    def run ( self ):
        while True: #send 1,2,3 in a loop
            if random.random() < .5:
                self.state_control.win_keyboard_input(96)
            else:
                self.state_control.win_keyboard_input(97)
            time.sleep(1)
            for k in xrange(98,100): 
                self.state_control.win_keyboard_input(k)
                time.sleep(1)

