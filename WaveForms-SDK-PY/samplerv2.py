'''
AD2 sampler

Generates a pulse in the AnalogOut 1 channel and collects samples
in both scope channels with a trigger set on channel 1

Author: Nick Sanders

Waveforms SDK Documentation:
https://digilent.com/reference/software/waveforms/waveforms-sdk/reference-manual

To run:
python AD2_sampler.py <sample_rate (MHz)> <V_trig (V)> <nwaves> <name>
'''

import numpy as np
import sys
import time
from tqdm import tqdm
import matplotlib.pyplot as plt
from ctypes import *
sys.path.insert(0, 'C:/Program Files (x86)/Digilent/WaveFormsSDK/samples/py')
from dwfconstants import *
dwf = cdll.dwf

#sampling params
sample_rate = float(sys.argv[1]) * 1000000.0
V_trig = float(sys.argv[2])
Nwaves = int(sys.argv[3])
name = str(sys.argv[4])

nPerWave = 8000  #number of samples per waveform
nSamples = Nwaves * nPerWave  #total number of samples

#wavegen params
wave_freq = 500.0 #Hz
offset = 0.0 #V
amplitude = 0.25 #V

hdwf = c_int()  #Variable to hold device ID
sts = c_byte()  #Variable to hold status of trigger
rgdSamples1 = (c_double*nSamples)()  #Channel 1 buffer
rgdSamples2 = (c_double*nSamples)()  #Channel 2 buffer

print("Opening first device")
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))  #Open AD2

if hdwf.value == hdwfNone.value:
    szError = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szError);
    print("failed to open device\n"+str(szError.value))
    quit()
    
#set up wavegen
dwf.FDwfAnalogOutNodeEnableSet(hdwf, c_int(0), c_int(0), c_bool(True))
dwf.FDwfAnalogOutNodeFunctionSet(hdwf, c_int(0), c_int(0), funcSquare)
dwf.FDwfAnalogOutNodeFrequencySet(hdwf, c_int(0), c_int(0), c_double(wave_freq))
dwf.FDwfAnalogOutNodeOffsetSet(hdwf, c_int(0), c_int(0), c_double(offset))
dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, c_int(0), c_int(0), c_double(amplitude))
dwf.FDwfAnalogOutConfigure(hdwf, c_int(0), c_bool(True))

#set up acquisition
dwf.FDwfAnalogInFrequencySet(hdwf, c_double(sample_rate))
dwf.FDwfAnalogInBufferSizeSet(hdwf, c_int(nPerWave)) 
dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(0), c_bool(True))  #Enable Channel 1
dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(0), c_double(10))
dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(1), c_bool(True))  #Enable Channel 2
dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(1), c_double(10))

#set up trigger
dwf.FDwfAnalogInTriggerAutoTimeoutSet(hdwf, c_double(0))        #disable auto trigger
dwf.FDwfAnalogInTriggerSourceSet(hdwf, trigsrcDetectorAnalogIn) #trigger on the scope
dwf.FDwfAnalogInTriggerTypeSet(hdwf, trigtypeEdge)              #trigger on edge
dwf.FDwfAnalogInTriggerChannelSet(hdwf, c_int(0))               #trigger on channel 1
dwf.FDwfAnalogInTriggerLevelSet(hdwf, c_double(V_trig))         #set trigger threshold
dwf.FDwfAnalogInTriggerConditionSet(hdwf, DwfTriggerSlopeRise)  #trigger on rising slope

time.sleep(2) #wait for wavegen to stabilize

print("Starting repeated acquisitions")
dwf.FDwfAnalogInConfigure(hdwf, c_bool(False), c_bool(True))

all_data = np.zeros((2,Nwaves,nPerWave), dtype=float)  #array to save all data in

cSamples = 0
start = time.perf_counter()

'''
Collecting Triggered Samples
'''
while cSamples < nSamples:  #While there are still samples to collect
    dwf.FDwfAnalogInStatus(hdwf, c_int(1), byref(sts))  #Check status of trigger
    if sts.value != DwfStateDone.value:  #If not triggered, go to top of loop
        continue
    dwf.FDwfAnalogInStatusData(hdwf, c_int(0), byref(rgdSamples1, sizeof(c_double)*cSamples), c_int(nPerWave))  #get channel 1 data
    dwf.FDwfAnalogInStatusData(hdwf, c_int(1), byref(rgdSamples2, sizeof(c_double)*cSamples), c_int(nPerWave))  #get channel 2 data
    cSamples += nPerWave

end = time.perf_counter()
dwf.FDwfAnalogOutConfigure(hdwf, c_int(0), c_bool(False))  #Turn off wavegen
dwf.FDwfDeviceCloseAll()  #Disconnect AD2

print(f'Process took {end - start} seconds')
det_freq = Nwaves / (end - start)
det_eff = 1 - ((wave_freq - det_freq) / wave_freq)
print(f'Detection Efficiency = {det_eff}')

'''
Saving Data
'''
samplesArray1 = np.fromiter(rgdSamples1, dtype=float)
samplesArray2 = np.fromiter(rgdSamples2, dtype=float)
for i in range(Nwaves):
    left, right = i * nPerWave, (i+1) * nPerWave
    all_data[0,i,:] = samplesArray1[left:right]
    all_data[1,i,:] = samplesArray2[left:right]

np.save(f'./data/{name}.npy', all_data)