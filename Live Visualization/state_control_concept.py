"""
This file contains example code that will be rewritten into the master thread
for the biodata project

The idea is that we will have a master thread that will access the biodata_spacebrew_client,
whih is running its own thread and pushing the ecg and eeg data into a queue.
we can then pop that data from the spacebrew_client from within the master thread, and do the analysis there. This allows us to do heavy lifting outside of the handle_value() callback method in the spacebrew_client.
The master thread will the create JSON packets and send those to the visualization depending on the state of the system

Author: WatsonIX
Date: 2015.01.09
"""


import threading
from threading import Timer

#EXPERIMENT STATE CODES
NO_EXPERIMENT = 0
SETUP_INSTRUCTIONS = 10
SETUP_CONFIRMATION = 11
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

#time constants
baseline_instruction_seconds = 20
condition_instruction_seconds = 20
baseline_seconds = 30
condition_seconds = 90

# this gets called by the listener
def handle_network_input(type,value):
	if type == 'eeg_alpha':
		process_eeg_alpha(value)
	elif type == 'ecg_interval':
		# handle HR stuff
	else:
		raise Exception("Unknown network input type: {}".format(type))

def process_eeg_alpha(value):
	# log data
	# post to visulazation if in appropriate state %%%
	# devNote: possibly wait to post until have all packets for time point

def start_baseline_instructions():
	experiment_state = BASELINE_INSTRUCTIONS
	instruction_timer = Timer(baseline_instruction_seconds,start_baseline_collection) #*** devNote: may want to send a countdown to visualization
    instruction_timer.start()
    # send instructions command to vis %%%
    
def start_baseline_collection():
	experiment_state = BASELINE_COLLECTION
	baseline_timer = Timer(baseline_seconds,start_condition_instructions) #*** devNote: may want to send a countdown to visualization %%%
    baseline_timer.start()
    # trigger vis to start plotting %%%

def start_condition_instructions():


def keyboard_input():
	#devNote: could do this smarter by not calling this function unless in one of the appropriate states
	if experiment_state == SETUP_CONFIRMATION:
		input = ''
		while input != '1':
	    	print 'When you are set up and seated, type \'1\' and press enter'
		    input = raw_input()
		### select condition
		start_baseline_instructions()
	elif experiment_state == BASELINE_CONFIRMATION:
		### confirm valid trial, collect subjective info and proceed to condition
	elif experiment_state == CONDITION_CONFIRMATION:
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

#initialize
experiment_state = NO_EXPERIMENT
condition_state = NO_CONDITION

kInputThread = KeyboardInputThread()
kInputThread.start()
