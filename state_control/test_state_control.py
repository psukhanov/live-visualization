import time
from state_control import ChangeYourBrainStateControl
#import pycurl

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
		return 1


class ecg_real(object):

	from neurosky_ecg import NeuroskyECG
	import sys

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
		return self.cur_hrv


# c = pycurl.Curl()
# c.setopt(c.URL, ' http://cloudbrain.rocks/link?pub_metric=eeg&sub_metric=muse-001-eeg&publisher=muse-001&subscriber=booth-example&pub_ip=54.183.68.29&sub_ip=54.183.68.29')
# c.perform()

ecg = ecg_fake()
sc = ChangeYourBrainStateControl('blah', None, ecg=ecg, vis_period_sec = .25, baseline_sec = 5, condition_sec = 5, baseline_inst_sec = 2, condition_inst_sec = 2)
sc.tag_in()