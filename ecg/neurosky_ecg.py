# -*- coding: utf-8 -*-
"""
NeuroSky ECG algorithm library

This python module serves as a wrapper around the C library, giving efficent access
to the library methods used to record and analyze ECG data, obtained with the
NeuroSky CardioChip


Created on Wed Jan 14 17:37:11 2015

@author: mpesavento
"""

from ctypes import cdll, c_double

from threading import Thread
import sys
import os
import time
import random
import serial
from Queue import Queue




SYNC_BYTE   = 0xAA #NOTE: this used to be 0x77!!! change this in the documentation
EXCODE_BYTE = 0x55
# single-byte codes
SENSOR_STATUS = 0x02
HEART_RATE  = 0x03
CONFIG_BYTE = 0x08
# multi-byte codes
RAW_ECG = 0x80
DEBUG_1 = 0x84 # not used
DEBUG_2 = 0x85 # not used



class NeuroskyECG(object):
    """ 
    This class creates a Producer/Consumer model that allows asynchronous
    updating of live ECG data through a serial port, namely one connected
    to the cardioChip Starter Kit via bluetooth

    The class maintains an internal queue of the raw ecg values, and gives the user
    choice of how to proceed with processing the ECG data.
    Typically, if leadoff id detected, the user will not want to be repeatedly calling
    the analysis library. 
    Using a queue allows the user to throw away the leadoff data, and only analyze the 
    valid raw data.
    """
    

    def __init__(self, port='COM8', timeout=2):
        self.connected = False
        self.port = port
        self.timeout= timeout
        self.baud = 57600
        self.Fs = 512 # cardiochip reports ecg values at a sample rate of 512 hz
        self.HRV_UPDATE = 1 # update the HRV between this many hear beats; eg if 2, we update hrv every 2 beats


        # CardioChip bluetooth auth key = 0000
        print "Connecting to NeuroSky CardioChip (%s)... " % self.port
        self.ser = serial.Serial(self.port, self.baud, timeout=self.timeout)

        self.ecg_buffer = Queue(0) # zero is infinite max queue length
        self.analyze = self._ecgInitAlgLib() #returns the C library object
        self.filter_delay = 242 # number of samples of delay, 242 for 60Hz filter, 308 for 50 Hz
        self.starttime = None #start time, in unix epoch seconds
        self.curtime = None


    def start(self):
        """
        starts a thread of the read_cardiochip() method
        """
        #TODO add thread checking, should only be 1 thread per serial interface
        self.connected = True
        t1 = Thread(target=self._read_cardiochip)  
        t1.daemon = True
        t1.start()
        print "Started CardioChip reader"   


    def check(self):
        """ checks if thread currently exists """
        return self.connected


    def stop(self):
        """ stops running thread """
        self.connected = False  

    def setHRVUpdate(self, numRRI):
        """ 
        set the number of RR intervals to count
        between updating the HRV value
        """
        self.HRV_UPDATE = numRRI

    def _parseData(self, payload):
        """
        given the byte payload from the serial connection, parse the first byte
        as the code and return a list of dicts of all values found in the packet
        dicts will be of the format: {'timestamp', t, <codename>: codeval}

        Timestamps are based on the first raw_ecg data received on the host computer, and
        extrapolated using a sample frequency of 512 Hz from there. This is accurate in the short term,
        but should not be used for longer (>10 min) recordings.
        """
        out=[]
        bytesParsed = 0
        while bytesParsed < len(payload):

            #check for the extended Code Level, code and length
            #count the number of EXCODE_BYTE
            #extendedCodeLevel = sum([1 for x in data if x == EXCODE_BYTE] )
            #bytesParsed += extendedCodeLevel

            #identify the length of the expected bytes in the payload
            code = payload[bytesParsed]
            bytesParsed +=1
            if code > 0x7F:
                # multi-byte code, length > 1
                length = payload[bytesParsed]
                bytesParsed +=1
            else:
                length = 1

            if code == SENSOR_STATUS:
                # value of 0==no contact, 200==contact
                #print "leadoff: %i" % payload[bytesParsed]
                out.append( {'timestamp': self.curtime, 'leadoff': payload[bytesParsed] } )
                bytesParsed +=1

            elif code == HEART_RATE:
                #print "HR: %i" % payload[bytesParsed]
                out.append( {'timestamp': self.curtime, 'HR': payload[bytesParsed:] } )
                bytesParsed +=1

            elif code == CONFIG_BYTE:
                #print "config: %i" % payload[bytesParsed]
                out.append( {'timestamp': self.curtime, 'config': payload[bytesParsed:] } )
                bytesParsed +=1

            elif code == RAW_ECG:
                # raw value is between -32768 and 32767, in twos compliment form
                # if the raw value is higher than 32768, it should be rolled around to allow for negative values
                raw = payload[bytesParsed]*256 + payload[bytesParsed]
                if raw >= 32768: 
                    raw = raw - 65536
                #print "ecg: %i" % ecg

                # create the timestamp on each ECG sample, starting from the first
                if self.starttime is None:
                    self.starttime = time.time()
                    self.curtime = self.starttime
                else:
                    self.curtime = self.curtime + 1./self.Fs

                out.append( {'timestamp': self.curtime, 'ecg_raw': raw } )
                bytesParsed += length

            elif code == DEBUG_1:
                #print "debug1: " + str(payload[bytesParsed:]).strip('[]')
                out.append( {'timestamp': self.curtime, 'debug1': payload[bytesParsed:] } )
                bytesParsed += length

            elif code == DEBUG_2:
                #print "debug2: " + str(payload[bytesParsed:]).strip('[]')
                out.append( {'timestamp': self.curtime, 'debug2': payload[bytesParsed:] } )
                bytesParsed += length

            else:
                print "unknown code: %i" % code

        return out


    def _read_cardiochip(self):
        """
        read data packets from the cardiochip starter kit, via the bluetooth serial port
        """
        cur_leadstatus = 0
        sample_count =0
        while self.connected:
            sample_count+=1
            #check for sync bytes
            readbyte = ord(self.ser.read(1))
            #print readbyte, SYNC_BYTE
            if readbyte != SYNC_BYTE:
                continue
            readbyte = ord(self.ser.read(1))
            if readbyte != SYNC_BYTE:
                continue

            #parse length byte
            while True:
                pLength = ord(self.ser.read(1))
                if pLength != SYNC_BYTE:
                    break
            if pLength > 169:
                continue
            #print "L: %i" % pLength

            # collect payload bytes
            payload = self.ser.read(pLength)
            payload = [ord(x) for x in payload] #convert to int from string
            #print "payload: " + str(payload).strip('[]')
            # ones complement inverse of 8-bit payload sum
            checksum = sum(payload) & 0xFF
            checksum = ~checksum & 0xFF

            # catch and verify checksum byte
            chk = ord(self.ser.read(1))
            #print "chk: " + str(checksum)
            if chk != checksum:
                print "checksum error, %i != %i" % (chk, checksum)
                continue

            output = self._parseData(payload)

            lead_status  = next(( d for d in output if 'leadoff' in d), None)
            if lead_status is not None:
                #print lead_status
                #if cur_leadstatus != lead_status['leadoff']:
                #    print " LEAD CHANGE ================================="
                if cur_leadstatus != lead_status['leadoff']:
                    #we have a change
                    if lead_status['leadoff']==200:
                        print "LEAD ON"
                    elif lead_status['leadoff']==0:
                        print "LEAD OFF"
                cur_leadstatus = lead_status['leadoff']

            # store the output data in a queue
            # first, create a tuple with the sample index and dict with the timestamp and ecg
            ecgdict = next(((i,d) for i,d in enumerate(output) if 'ecg_raw' in d), None)
            if ecgdict is not None and sample_count>self.Fs*2:
                #let's just ignore the first 2 seconds of crappy data
                ecgdict[1]['leadoff'] = cur_leadstatus
                #print ecgdict[1]
                self.ecg_buffer.put(ecgdict[1]) # this should save the ecg and timestamp keys

        return


    def isBufferEmpty(self):
        """ check to see if ecg buffer is empty """
        return self.ecg_buffer.empty()

    def popBuffer(self):
        """ get first value  (dict) in the ecg_buffer """
        return self.ecg_buffer.get()


    def _ecgInitAlgLib(self,libname='TgEcgAlg64.dll', power_frequency=60):
        """ initialize the TgEcg algorithm dll """
        print "loading analysis library: " + libname
        E = cdll.LoadLibrary(libname)
        
        E.tg_ecg_do_hrv_sdnn(0)
        E.tg_ecg_do_relaxation_level(0)
        E.tg_ecg_do_respiratory_rate(0)
        E.tg_ecg_do_rri_precise(0)
        E.tg_ecg_set_power_line_freq(power_frequency)
        E.tg_ecg_get_raw_smoothed.restype = c_double
        E.tg_ecg_init() # init the library with selected options
        return E
        
    def ecgResetAlgLib(self):
        """ reset ecg algorithm """
        print "resetting ecg analysis library"
        self.analyze.tg_ecg_init()

    def getTotalNumRRI(self):
        """
        return the total number of RRIs held in the algorithm buffer
        """
        return self.analyze.tg_ecg_get_total_rri_count()


    def ecgalgAnalyzeRaw(self, D): #, dataqueue):
        """
        test to see if we have values in the ecg_buffer, and if so, pass
        the most recent raw_ecg value into the TgEcg analysis framework
        Returns dict with timestamp, filtered ECG, HR, and HRV, if available

        This function expects a dict as input, with keys
        """
        #D = self.popBuffer()
        self.analyze.tg_ecg_update(D['ecg_raw'])
        #ecg_filt = self.analyze.tg_ecg_get_raw_filtered() #delayed against raw by 211 samples
        ecg_filt = self.analyze.tg_ecg_get_raw_smoothed() #delayed against raw by 450 samples, if 60Hz powerline
        D['ecg_filt']= ecg_filt

        if self.analyze.tg_ecg_is_r_peak():
            #print "found peak"
            num_rri = self.analyze.tg_ecg_get_total_rri_count() 
            rri = self.analyze.tg_ecg_get_rri()
            hr = self.analyze.tg_ecg_compute_hr_now()
            D['rri']= rri
            D['hr'] = hr
            print "%i HR: %i (rri: %i)" % (num_rri, 60000* 1/rri, rri)
            if num_rri >= 30 and (num_rri+2) % self.HRV_UPDATE == 0: 
                #calculate every 4 heartbeats, starting at 30
                hrv = self.analyze.tg_ecg_compute_hrv(30)
                D['hrv'] = hrv
                print "hrv: " + str(hrv)

        return D



if __name__ == "__main__":
    ### all of the code below is used for visualization and testing of the ECG framework
    ### not to be used as production code, but can be used for examples on how to use
    ### the NSK framework
    import numpy as np
    #from matplotlib import pyplot as plt
    import pylab as plt

    # hack to get interactive plot working
    # https://github.com/matplotlib/matplotlib/issues/3505
    sys.ps1 = 'IAMAHACK'


    target_port = 'COM8'

    plot_fig=True

    ecgdict = []

    try:
        nskECG = NeuroskyECG(target_port)
    except serial.serialutil.SerialException:
        print "Could not open target serial port: %s" % target_port
        sys.exit(1)

    nskECG.start()

    if plot_fig:
        plt.ion()
        #load the queues to plot
        # t = [ x/nskECG.Fs for x in range(0,nskECG.Fs*1)]
        # ecgval = [0]*nskECG.Fs*1
        t=[time.time()]
        ecgval =[0]

        #set up the test plot
        fig = plt.figure(figsize=(12,8))
        ax1 = fig.add_subplot(2,1,1) #smoothed ECG
        #ecgtrace, = plt.plot(0,0)
        ecgtrace, = plt.plot(t,ecgval)
        ax1.set_ylim((-10000, 10000))

        ax2 = fig.add_subplot(2,1,2) # HRV
        hrvtrace, = ax2.plot(t,[0])
        ax2.set_ylim((0, 300))

        time.sleep(0.1)

    ##########################################
    sample_count = 0
    leadoff_count = 0
    isreset=False
    while True:
        if not nskECG.isBufferEmpty():
            sample_count+=1
            #print "buffer len", nskECG.ecg_buffer.qsize()
            D = nskECG.popBuffer()
            # ignore data prior to leadoff

            if D['leadoff']==0 and sample_count > nskECG.Fs*2:
                leadoff_count+=1
                #print "leadoff", D['leadoff']
                if leadoff_count>nskECG.Fs*2: #more than 2 seconds of leadoff, drop them
                    #if not isreset: # we haven't reset recently, DO IT
                    if nskECG.analyze.tg_ecg_get_total_rri_count()!=0:
                        isreset = True
                        ecgdict = [] #reset the buffer
                        nskECG.ecgResetAlgLib()
                        print "num rri post reset", nskECG.analyze.tg_ecg_get_total_rri_count()
                    nskECG.ecg_buffer.task_done()
                    continue
            else: # leadoff==200, or lead on
                #print "done resetting, loading data again"
                leadoff_count=0
                if isreset:
                    print "turning things back on"
                    isreset = False

            D = nskECG.ecgalgAnalyzeRaw(D)

            ### the next two lines are examples of how to pop values from the
            #   internal buffer and create a list of filtered ecg values.
            #   You can do the same thing for 'rri' and 'hrv' values
            #   I would also keep track of the unix timestamp, to make sure it lines up
            #   with the EEG timestamps
            #minibuffer = [nskECG.popBuffer() for i in range(0,nskECG.Fs/4.)]
            #ecgfilt = [x['ecg_filt'] for x in minibuffer]
            #if 'hrv' in D:
            #    cur_hrv=D['hrv']

            ecgdict.append(D)
            #print D

            #########################################
            # plot the data

            if plot_fig and sample_count%64==0:
                #print "length ecgdict", len(ecgdict),  -min([len(ecgdict),512*4])
                ecgsub = ecgdict[-min([len(ecgdict),nskECG.Fs*4]):]

                ecg_t = [x['timestamp'] for x in ecgsub]
                ecg_filt = [x['ecg_filt'] for x in ecgsub]

                ymin = float(min(ecg_filt))-100
                ymax = float(max(ecg_filt))+100
                plt.axes(ax1)
                ax1.set_ylim((ymin,ymax))
                ecgtrace.set_xdata(ecg_t)
                ecgtrace.set_ydata(ecg_filt)

                ax1.relim()
                ax1.autoscale_view()

                #################
                # update hrv
                hrv_t=[x['timestamp'] for x in ecgsub if 'hrv' in x]
                hrv =[x['hrv'] for x in ecgsub if 'hrv' in x]

                if len(hrv) != 0:
                    #print "length hrv", hrv
                    plt.axes(ax2)
                    ymin = float(min(hrv))-10
                    ymax = float(max(hrv))+10
                    ax2.set_ylim((ymin,ymax))
                    hrvtrace.set_xdata(hrv_t)
                    hrvtrace.set_ydata(hrv)
                    ax2.relim()
                    ax2.autoscale_view()
                
                #if sample_count%256==0:
                #    time.sleep(0.05)
                plt.draw()

            #let the queue know we are done processing its 
            nskECG.ecg_buffer.task_done()

    # stop the thread, ctrl-C
    pass
