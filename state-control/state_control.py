# NOTE THIS HAS NOT BEEN RUN! 

import threading
from threading import Timer
import time
import json

#EXPERIMENT STATE CODES
NO_EXPERIMENT = 0
SETUP_INSTRUCTIONS = 10
BASELINE_INSTRUCTIONS = 21
BASELINE_COLLECTION = 22
BASELINE_CONFIRMATION = 23
CONDITION_INSTRUCTIONS = 31
CONDITION_COLLECTION = 32
CONDITION_CONFIRMATION = 33
POST_EXPERIMENT = 50

#CONDITION STATE CODES
NO_CONDITION = 100
BREATHING = 101
VIPASSANA = 102
ZEN = 103

class ChageYourBrainStateControl():

    def __init__(self,client_name,sb_server, vis_period_sec = .25, baseline_sec = 30, condition_sec = 90, baseline_inst_sec = 20, condition_inst_sec = 20):
    	self.client_name = ###
    	self.sb_server = ###
		self.experiment_state = NO_EXPERIMENT
		self.condition_state = NO_CONDITION
		self.tag_time = 0 #last time someone tagged in
		self.vis_period = vis_period_sec
		self.baseline_seconds = baseline_sec
		self.condition_seconds = baseline_sec
		self.baseline_instruction_seconds = baseline_inst_sec 
		self.condition_instruction_seconds = condition_inst_sec

		self.kInputThread = KeyboardInputThread()
		self.kInputThread.start()

		self.alpha_buffer = []
		self.hrv_last = 0

		### start / reset a whole uptime timer 

	### CALLED VIA SPACEBREW CLIENT LISTENER ############
	def process_eeg_alpha(self,value):
		self.alpha_buffer.append(value)
		### make sure buffer gets clear when no subjects
		### log data
		
	def process_ecg(self,lead_on,hrv):
		#devNote: for moment, assuming we're definitely getting only (LED,HRV) values. in future 1st int may indicate lead on/off X values to expect
		if self.experiment_state == NO_EXPERIMENT:
			pass
		elif self.experiment_state == SETUP_INSTRUCTIONS:
		elif self.experiment_state == BASELINE_INSTRUCTIONS:
			if hrv:
				self.hrv_last = hrv
		### log data
		self.hrv_save['time'].append(time.time())

	def tag_in(self):
		#devNote: put here possible confirmation of user change if in middle of experiment
		start_setup_instructions()
		self.tag_time = time.time()

		### start / reset a whole experiment timer + list of state times
		### save logged data and reset variables
		self.alpha_save = {'time': [], 'value':[]]
		self.hrv_save = {'time': [], 'value': []}

	######################################################
	### STATE CHANGING ############
	def start_setup_instructions(self):
		#devNote: possibly add both time-in and time-out timer here which takes us back to (no experiment)
		self.experiment_state = SETUP_INSTRUCTIONS
		### change instructions to new style
        instruction = {"message": {
            "value" : "SETUP_INSTRUCTIONS",
            "type": "string", "name": "instruction", "clientName": self.client_name}}    
        self.sb_server.ws.send(json.dumps(instruction))
        ### do_while_every looking for lead_on
			if lead_on:
				start_baseline_instructions()

	def start_baseline_instructions(self):
		self.experiment_state = BASELINE_INSTRUCTIONS
		instruction_timer = Timer(baseline_instruction_seconds,start_baseline_collection) #*** devNote: may want to send a countdown to visualization
	    instruction_timer.start()
	    output_instruction()
	    
	def start_baseline_collection(self):
		self.experiment_state = BASELINE_COLLECTION
		baseline_timer = Timer(self.baseline_seconds,start_post_baseline) #*** devNote: may want to send a countdown to visualization %%%
	    baseline_timer.start()
	    do_every_while(self.vis_period,BASELINE_COLLECTION,output_baseline) # instruct vis to start plotting 

    def start_post_baseline(self):
    	"""ask for confirmation + subjective feedback + selection of condition"""
		self.experiment_state = BASELINE_CONFIRMATION
		### confirm
		### collect subj info
		### choose condition
    	###*** how to collect this keyboard input if window focus is not on console!??? 
    	start_condition_instructions()

	def start_condition_instructions(self):
		### differentiate between the three possible conditions (currently assuming breathing)
		self.experiment_state = CONDITION_INSTRUCTIONS
		instruction_timer = Timer(baseline_instruction_seconds,start_condition_collection) #*** devNote: may want to send a countdown to visualization
	    instruction_timer.start()
	    output_instruction()

	def start_condition_collection(self):
		self.experiment_state = CONDITION_COLLECTION
		condition_timer = Timer(self.condition_seconds,start_post_condition) #*** devNote: may want to send a countdown to visualization %%%
	    condition_timer.start()
	    ### ??? send instructor
	    do_every_while(self.vis_period,CONDITION_COLLECTION,output_condition) # instruct vis to start plotting 

    def start_post_condition(self):
    	"""ask for confirmation + subjective feedback"""
		self.experiment_state = CONDITION_CONFIRMATION
		### choose condition
		### confirm
	    output_instruction('CONFIRMATION')
	    time.sleep(1)
		### collect subj info
	    output_instruction('Q1')
	    time.sleep(1)
	    output_instruction('Q2')
	    time.sleep(1)
	    output_instruction('Q3')
    	###*** how to collect this keyboard input if window focus is not on console!??? 

    def start_post_experiment(self):
    	"""display aggregates and wait for new tag in!"""
		self.experiment_state = NO_EXPERIMENT

	######################################################
	### SEND TO VISUALIZTION #############################

	def output_instruction(self,sub_state=None):
		if self.experiment_state == BASELINE_INSTRUCTIONS:
			instruction_text = ###
		if self.experiment_state == CONDITION_INSTRUCTIONS:
			instruction_text = ###
		if self.experiment_state in [CONDITION_CONFIRMATION,BASELINE_CONFIRMATION]:
			if sub_state == "CONFIRMATION" and self.experiment_state == BASELINE_CONFIRMATION:
				instruction_text = ###
			elif sub_state == "CONFIRMATION" and self.experiment_state == CONDITION_CONFIRMATION:
				instruction_text = ###
			elif sub_state == "Q1":
				instruction_text = ###
			elif sub_state == "Q2":
				instruction_text = ###
			elif sub_state == "Q3":
				instruction_text = ###
			else:
				raise Exception ('Unkown sub_state for instruction sent in state ' + str(self.experiment_state)

		instruction = {"message": {
            "value" : {'instruction_name': 'DISPLAY_INSTRUCTION', 'instruction_text': instruction_text},
            "type": "string", "name": "instruction", "clientName": self.client_name}}    
        self.sb_server.ws.send(json.dumps(instruction))

	def output_baseline(self):
		"""output aggregated EEG and HRV values"""
		#devNote: possibly switch to outputting raw ECG instead of HRV during baseline
		if self.alpha_buffer:
			alpha_out = mean(self.alpha_buffer)
			self.alpha_save['time'].append(time.time())
			self.alpha_save['value'].append(alpha_out)
		else: 
			alpha_out = 0
		self.alpha_buffer = []

		value_out = "{:.2f},{:.2f},{:.1f}".format(alpha_out,self.hrv_last,time.time()-self.tag_time)
        message = {"message": { #send synced EEG & ECG data here
            "value": value_out,
            "type": "string", "name": "EEG_ECG", "clientName": self.client_name}}
        self.sb_server.ws.send(json.dumps(message))


	def output_condition_instructions(self):
		instruction = {"message": {
            "value" : "CONDITION_INSTRUCTIONS",
            "type": "string", "name": "instruction", "clientName": self.client_name}}    
        self.sb_server.ws.send(json.dumps(instruction))



	######################################################
	### HELPER #############################

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
			time.sleep(g.next())
			f(*args)


	def keyboard_input(self):
		#devNote: could do this smarter by not calling this function unless in one of the appropriate states
		if self.experiment_state == SETUP_CONFIRMATION:
			input = ''
			while input != '1':
		    	print 'When you are set up and seated, type \'1\' and press enter'
			    input = raw_input()
			### select condition
			start_baseline_instructions()
		elif self.experiment_state == BASELINE_CONFIRMATION:
			### confirm valid trial, collect subjective info and proceed to condition
		elif self.experiment_state == CONDITION_CONFIRMATION:
			### confirm valid trial, collect subjective info and proceed to final display %%%
		#(otherwise do nothing!)

class KeyboardInputThread ( threading.Thread ):
    
    def __init__(self):
        super(KeyboardInputThread, self).__init__()
        self.running = True

    def stop ( self ):
        self.running = False

    def run ( self ):
        while self.running:
            keyboard_input()

