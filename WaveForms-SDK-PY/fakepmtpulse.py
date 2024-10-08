from WF_SDK import device, scope, wavegen, tools, error
import numpy as np
import matplotlib.pyplot as plt
import ctypes
from sys import platform
from time import sleep

if platform.startswith("win"):
    dwf = ctypes.cdll.dwf
elif platform.startswith("darwin"):
    dwf = ctypes.cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = ctypes.cdll.LoadLibrary("libdwf.so")

# Pulse parameters
min_amplitude = 250e-3  # 250 mV
max_amplitude = 800e-3  # 800 mV
pulse_width = 700e-9
tau_rise = 100e-9
tau_fall = 200e-9

# Time vector
t = np.linspace(0, 3*pulse_width, 1000)

# Modified Gaussian function
def pulse(t, amplitude, tau_rise, tau_fall):
    p = (1 - np.exp(-t/tau_rise)) * np.exp(-t/tau_fall)
    p = p - np.mean(p)
    return -amplitude * p / np.max(np.abs(p))

# Function to generate random pulse amplitude
def random_amplitude():
    scale = (max_amplitude - min_amplitude) / 2  # Adjust scale as needed
    amplitude = np.random.exponential(scale)
    return np.clip(amplitude, min_amplitude, max_amplitude)

try:
    # Enumerate devices
    device_count = ctypes.c_int()
    dwf.FDwfEnum(scope.constants.enumfilterAll, ctypes.byref(device_count))

    if device_count.value == 0:
        raise error("No device found")

    # Open the first device
    hdwf = ctypes.c_int()
    dwf.FDwfDeviceOpen(ctypes.c_int(0), ctypes.byref(hdwf))

    # Prepare the device data structure
    device_data = device.data()
    device_data.handle = hdwf.value

    # Initialize the wavegen with default settings
    wavegen.enable(device_data, channel=1)

    print("Generating pulses with random amplitudes...")

    num_pulses = 50  # Number of pulses
    for i in range(num_pulses):
        pulse_amplitude = random_amplitude()
        
        # Generate pulse data
        pulse_data = pulse(t, pulse_amplitude, tau_rise, tau_fall)

        # Prepare the pulse data for the wavegen
        mydata = (ctypes.c_double * len(pulse_data))(*pulse_data)

        # Configuring wavegen to output the pulse
        wavegen.dwf.FDwfAnalogOutNodeEnableSet(device_data.handle, ctypes.c_int(0), wavegen.constants.AnalogOutNodeCarrier, ctypes.c_bool(True))
        wavegen.dwf.FDwfAnalogOutNodeFunctionSet(device_data.handle, ctypes.c_int(0), wavegen.constants.AnalogOutNodeCarrier, wavegen.constants.funcCustom)
        wavegen.dwf.FDwfAnalogOutNodeDataSet(device_data.handle, ctypes.c_int(0), wavegen.constants.AnalogOutNodeCarrier, mydata, ctypes.c_int(len(pulse_data)))
        wavegen.dwf.FDwfAnalogOutNodeFrequencySet(device_data.handle, ctypes.c_int(0), wavegen.constants.AnalogOutNodeCarrier, ctypes.c_double(1 / (pulse_width)))
        wavegen.dwf.FDwfAnalogOutNodeAmplitudeSet(device_data.handle, ctypes.c_int(0), wavegen.constants.AnalogOutNodeCarrier, ctypes.c_double(pulse_amplitude))
        wavegen.dwf.FDwfAnalogOutConfigure(device_data.handle, ctypes.c_int(0), ctypes.c_bool(True))

        print(f"Generating pulse {i+1}/{num_pulses} with amplitude: {pulse_amplitude*1e3} mV")

        sleep(0.0001)  # pulse delay, 0.1 is 100 milliseconds

    # Stop the waveform
    wavegen.dwf.FDwfAnalogOutConfigure(device_data.handle, ctypes.c_int(0), ctypes.c_bool(False))

    # Close the device
    dwf.FDwfDeviceClose(hdwf)
    print("Pulse generation complete.")
except error as e:
    print(e)
    # Ensure the device is closed in case of error
    dwf.FDwfDeviceCloseAll()
