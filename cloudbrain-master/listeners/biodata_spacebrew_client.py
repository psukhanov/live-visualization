# add the shared settings file to namespace
import sys, random
import argparse
from os.path import dirname, abspath

sys.path.insert(0, dirname(dirname(abspath(__file__))))
import settings
from spacebrew.spacebrew import SpacebrewApp
import json
import time
from websocket import create_connection
import threading
from math import *
import webbrowser
#from state_control import ChangeYourBrainStateControl
from subprocess import call
from neurosky_ecg import NeuroskyECG
import sys
import serial

eeg_connect_string = "connect"
eeg_disconnect_string = "disconnect"

eeg_source = "fake" #fake or real
#eeg_source = "real" #fake or real

# ecg_source = "fake" #fake or real
ecg_source = "fake" #fake or real

if eeg_source == "real":
    serverName = "server.neuron.brain"
    port_no = 9000
else:
    serverName = '127.0.0.1'
    port_no = 9000

biodata_viz_url = 'file:///Users/paulsukhanov/Desktop/Explorabrainium/live-visualization-master/Live_Visualization/biodata_visualization.html'
#biodata_viz_url = 'file:///C:/Users/ExplorCogTech/src/live-visualization/Live_Visualization/biodata_visualization.html'

class SpacebrewClient(object):
    def __init__(self, name, server='127.0.0.1', port=9000): 
        self.server = server
        self.port = port
        self.timestamp = 0
        self.client_name = 'booth-7'

        # configure the spacebrew client
        self.brew = SpacebrewApp(name, server=server)
        self.osc_paths = [
            {'address': "/muse/eeg", 'arguments': 4},
            {'address': "/muse/eeg/quantization", 'arguments': 4},
            {'address': "/muse/eeg/dropped_samples", 'arguments': 1},
            {'address': "/muse/acc", 'arguments': 3},
            {'address': "/muse/acc/dropped_samples", 'arguments': 1},
            {'address': "/muse/batt", 'arguments': 4},
            {'address': "/muse/drlref", 'arguments': 2},
            {'address': "/muse/elements/low_freqs_absolute", 'arguments': 4},
            {'address': "/muse/elements/delta_absolute", 'arguments': 4},
            {'address': "/muse/elements/theta_absolute", 'arguments': 4},
            {'address': "/muse/elements/alpha_absolute", 'arguments': 4},
            {'address': "/muse/elements/beta_absolute", 'arguments': 4},
            {'address': "/muse/elements/gamma_absolute", 'arguments': 4},
            {'address': "/muse/elements/delta_relative", 'arguments': 4},
            {'address': "/muse/elements/theta_relative", 'arguments': 4},
            {'address': "/muse/elements/alpha_relative", 'arguments': 4},
            {'address': "/muse/elements/beta_relative", 'arguments': 4},
            {'address': "/muse/elements/gamma_relative", 'arguments': 4},
            {'address': "/muse/elements/delta_session_score", 'arguments': 4},
            {'address': "/muse/elements/theta_session_score", 'arguments': 4},
            {'address': "/muse/elements/alpha_session_score", 'arguments': 4},
            {'address': "/muse/elements/beta_session_score", 'arguments': 4},
            {'address': "/muse/elements/gamma_session_score", 'arguments': 4},
            {'address': "/muse/elements/touching_forehead", 'arguments': 1},
            {'address': "/muse/elements/horseshoe", 'arguments': 4},
            {'address': "/muse/elements/is_good", 'arguments': 4},
            {'address': "/muse/elements/blink", 'arguments': 1},
            {'address': "/muse/elements/jaw_clench", 'arguments': 1},
            {'address': "/muse/elements/experimental/concentration", 'arguments': 1},
            {'address': "/muse/elements/experimental/mellow", 'arguments': 1}
        ]


        print 'about to connect to %s' % self.server
        self.ws = create_connection("ws://%s:%s" % (self.server, self.port))

        print 'connected to server'
        for path in self.osc_paths:
            spacebrew_name = path['address'].split('/')[-1]
            #self.brew.add_subscriber(spacebrew_name, "string")
            #self.brew.subscribe(spacebrew_name, self.handle_value)   

        self.brew.add_publisher("eeg_ecg","string")
        self.brew.add_publisher("instruction","string")
        self.brew.add_subscriber("alpha_absolute","string")
        self.brew.add_subscriber(eeg_connect_string,"string")
        self.brew.add_subscriber(eeg_disconnect_string,"string")

    def set_handle_value(self,metric,handler):
        self.brew.subscribe(metric,handler)


    def handle_value(self, string_value):

        print "received string: %s" % string_value
        value = string_value.split(',')
        path = value[0]
        timestamp = value[5]

        '''if (int(timestamp) % 5 == 0):
            instruction = {"message": {
                "value" : {"instruction_name": "DISPLAY_INSTRUCTION", "instruction_text": "testing 1 2 3 yeah"},
                "type": "string", "name": "instruction", "clientName": self.client_name}}
        
            sb_server_2.ws.send(json.dumps(instruction))'''

        #print "path: %s" % path

        if path == "alpha_absolute":
            self.timestamp+=1 #should start incrementing (internal) timestamps after we've acquired signal from both EEG and ECG
            ecg = random.random();
            value_out = [timestamp] + [(float(value[2])+float(value[3]))/2] + [ecg]
            message = {"message": { #send synced EEG & ECG data here
                "value": value_out,
                "type": "string", "name": "eeg_ecg", "clientName": self.client_name}}
            instruction = {"message": {
                "value" : "BASELINE_INSTRUCTIONS",
                "type": "string", "name": "instruction", "clientName": self.client_name}}


            sb_server_2.ws.send(json.dumps(message))
            #sb_server.ws.send(json.dumps(instruction))

    def start(self):
        self.brew.start()

    def tag_in():
        print 'tagged in'

class SpacebrewServer(object):
    def __init__(self, muse_ids=['fake-muse'], server='127.0.0.1', port=9000):
        self.server = server
        self.port = port
        self.muse_ids = muse_ids
        self.osc_paths = [
            {'address': "/muse/elements/alpha_absolute", 'arguments': 4},
        ]

        self.ws = create_connection("ws://%s:%s" % (self.server, self.port))

        if(port==9000): #if this is the main server instance

            for muse in muse_ids:
                config = {
                    'config': {
                        'name': muse,
                        'publish': {
                            'messages': [{'name': name['address'].split('/')[-1], 'type': 'string'} for name in self.osc_paths]
                        }
                    }
                }
            self.ws.send(json.dumps(config))    
        
        elif (port==9002):
            config = {
                    'config': {
                        'name': 'booth-7',
                        'publish': {
                            'messages': [{'name': 'eeg_ecg', 'type' : 'string'},{'name' : 'instruction', 'type' : 'string'}]
                     }
                    }   
                }
            self.ws.send(json.dumps(config))    

    def start(self):
        time_stamp = 0
        while 1:
            time_stamp+=1
            time.sleep(0.1)
            for muse_id in self.muse_ids:
                for path in self.osc_paths:
                    metric = path['address'].split('/')[-1]
                    nb_args = path['arguments']

                    value = "%s,%s,%s,%s,%s" % (random.random(),random.random(),random.random(),random.random(), time_stamp)

                    message = {"message": {
                        "value": value,
                        "type": "string", "name": metric, "clientName": muse_id}}    
                    self.ws.send(json.dumps(message))



class ecg_fake():

    def __init__(self):
        self.lead_count = 0
        
    def is_lead_on(self):
        self.lead_count += 1
        if self.lead_count > 5:
            print 'lead on'
            return True
        else:
            print 'lead off'
            return False

    def get_hrv(self):
        return random.random()

class ecg_real(object):


    def __init__(self):

        self.lead_count = 0
        
        target_port = 'COM3'
        #target_port = 'devA/tty.XXXXXXX'  #change this to work on OSX

        try:
            self.nskECG = NeuroskyECG(target_port)
        except serial.serialutil.SerialException:
            print "Could not open target serial port: %s" % target_port
            sys.exit(1)

        #optional call, default is already 1
        self.nskECG.setHRVUpdate(1) #update hrv every 1 detected pulses

        self.cur_lead_on = False
        self.cur_hrv = 0


    def start(self):
        # start running the serial producer thread
        self.nskECG.start()

        # this loop is the consumer thread, and will pop 
        # dict values (with 'timestamp', 'ecg_raw', and 'leadoff'
        # from the internal buffer and run the analysis on the 
        # data.

        self.cur_hrv = None #whatever the current hrv value is
        self.cur_hrv_t = None #timestamp with the current hrv

        sample_count = 0 #keep track of numbers of samples we've processed
        leadoff_count = 0 #counter for length of time been leadoff
        while True:
            if not self.nskECG.isBufferEmpty():
                sample_count+=1
                D = self.nskECG.popBuffer() #get the oldest dict

                # if we are more than 2 seconds in and leadoff is still zero
                if D['leadoff']==0:
                    leadoff_count+=1
                    if leadoff_count> self.nskECG.Fs*2:
                        if self.nskECG.getTotalNumRRI()!=0:
                            #reset the library
                            self.nskECG.ecgalgResetLib()
                        self.nskECG.ecg_buffer.task_done() #let queue know that we're done
                        continue
                else: # leadoff==200, or lead is on
                    leadoff_count=0

                D = self.nskECG.ecgalgAnalyzeRaw(D)

                self.cur_lead_on = D['leadoff']
                if 'hrv' in D:
                    self.cur_hrv = D['hrv']
                    self.cur_hrv_t = D['timestamp']

            # we keep looping until something tells us to stop
        pass #      

    def is_lead_on(self):
        return self.cur_lead_on

    def get_hrv(self):
        if self.cur_hrv:
            return self.cur_hrv
        else:
            return 0

class ServerThread ( threading.Thread ):
    
    def __init__(self):
        super(ServerThread, self).__init__()
        self.running = True

    def stop ( self ):
        self.running = False

    def run ( self ):
        sb_server.start()

class ListenerThread (threading.Thread ):
    def __init__(self):
        super(ListenerThread, self).__init__()
        self.running = True

    def stop ( self ):
        self.running = False

    def run ( self ):
        sb_client.start()

parser = argparse.ArgumentParser(
    description='Receive data from Spacebrew.')
parser.add_argument(
    '--name',
    help='Your name or ID without spaces or special characters',
    default='7') #biodata is booth-7

if __name__ == "__main__":

    print 'servername: %s' % serverName

    global sb_server #Not sure if this needs to be a global or can be made a property of a biodata_client class
    sb_server = SpacebrewServer(muse_ids=['fake-muse'], server='127.0.0.1') #simulating data coming in from our user's muse

    serverThread = ServerThread()

    if eeg_source == 'fake':
        serverThread.start()

    global sb_server_2 # used for sending out instructions & processed EEG/ECG to the viz
    sb_server_2 = SpacebrewServer(server='127.0.0.1',port=9002,muse_ids=['booth-7'])

    print 'hello world 1'

    global sb_client
    args = parser.parse_args()
    sb_client = SpacebrewClient('booth-%s' % args.name, server=serverName,port=port_no) #in production, this will be set to server.neuron.brain

    listenerThread = ListenerThread()
    listenerThread.start()

    if (ecg_source == 'real'):
        ecg = ecg_real()
        t1 = threading.Thread(target=ecg.start)  
        t1.daemon = False
        t1.start()
    else:
        ecg = ecg_fake()

    print 'hello world 2'

    #file_dir = os.path.dirname(os.path.realpath(__file__))

    #hard-coding is bad! Somebody who knows python please find this file the right way 

    print 'hello world 3'

    if sys.platform == 'win32': #windoze
        chrome_path = 'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe %s'
    elif sys.platform == 'darwin': # MAC OSX
        chrome_path = 'open -a /Applications/Google\ Chrome.app %s'
    else: # Linux
        chrome_path = '/usr/bin/google-chrome %s'

    print 'hello world 4'

    #webbrowser.get(chrome_path).open(biodata_viz_url)    
    webbrowser.open(biodata_viz_url)    
    #time.sleep(4)

    sc = ChangeYourBrainStateControl(sb_client.client_name, sb_server_2, ecg=ecg, vis_period_sec = .25, baseline_sec = 10, condition_sec = 10, baseline_inst_sec = 5, condition_inst_sec = 8)
    print 'hello world 5'
    sb_client.set_handle_value('alpha_absolute',sc.process_eeg_alpha)

    if (eeg_source == 'real'):
        sb_client.set_handle_value(eeg_connect_string,sc.tag_in)
    else:
        time.sleep(4)
        sc.tag_in()
    
    print 'attempting to tag in'


    
