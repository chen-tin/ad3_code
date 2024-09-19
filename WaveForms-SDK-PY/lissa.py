from WF_SDK import device, scope, wavegen, tools, error
import numpy as np
import matplotlib.pyplot as plt
import ctypes
from sys import platform
from os import sep
from time import sleep

# Load the appropriate library based on the platform
if platform.startswith("win"):
    dwf = ctypes.cdll.dwf
elif platform.startswith("darwin"):
    dwf = ctypes.cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = ctypes.cdll.LoadLibrary("libdwf.so")

# Pulse parameters
pulse_amplitude = 300e-3  # 300 mV
a = 3
b = 4
delta = np.pi / 2

# Time vector
t = np.linspace(0, 1, 1000)  # Normalized time vector

# Lissajous function
def lissajous(t, amplitude, a, b, delta):
    x = amplitude * np.sin(a * t + delta)
    y = amplitude * np.sin(b * t)
    return y

# Generate Lissajous curve data
pulse_data = lissajous(t, pulse_amplitude, a, b, delta)

# Plot the Lissajous curve (optional)
plt.figure(figsize=(6, 6))
plt.plot(pulse_data, pulse_amplitude * np.sin(a * t + delta), color='red')
plt.title(r'Lissajous Curve: $\delta=\frac{\pi}{2}$, $a=3$, $b=4$')
plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True)
plt.show()

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

    # Prepare the pulse data for the wavegen
    mydata = (ctypes.c_double * len(pulse_data))(*pulse_data)

    # Configure the wavegen to output the pulse
    wavegen.dwf.FDwfAnalogOutNodeEnableSet(device_data.handle, ctypes.c_int(0), wavegen.constants.AnalogOutNodeCarrier, ctypes.c_bool(True))
    wavegen.dwf.FDwfAnalogOutNodeFunctionSet(device_data.handle, ctypes.c_int(0), wavegen.constants.AnalogOutNodeCarrier, wavegen.constants.funcCustom)
    wavegen.dwf.FDwfAnalogOutNodeDataSet(device_data.handle, ctypes.c_int(0), wavegen.constants.AnalogOutNodeCarrier, mydata, ctypes.c_int(len(pulse_data)))
    wavegen.dwf.FDwfAnalogOutNodeFrequencySet(device_data.handle, ctypes.c_int(0), wavegen.constants.AnalogOutNodeCarrier, ctypes.c_double(1))  # Adjust frequency as needed
    wavegen.dwf.FDwfAnalogOutNodeAmplitudeSet(device_data.handle, ctypes.c_int(0), wavegen.constants.AnalogOutNodeCarrier, ctypes.c_double(pulse_amplitude))
    wavegen.dwf.FDwfAnalogOutConfigure(device_data.handle, ctypes.c_int(0), ctypes.c_bool(True))

    print("Generating Lissajous curve pulse...")

    # Keep the waveform running for 20 seconds
    sleep(20)

    # Stop the waveform
    wavegen.dwf.FDwfAnalogOutConfigure(device_data.handle, ctypes.c_int(0), ctypes.c_bool(False))

    # Close the device
    dwf.FDwfDeviceClose(hdwf)
    print("Pulse generation done!")
except error as e:
    print(e)
    # Ensure the device is closed in case of error
    dwf.FDwfDeviceCloseAll()
