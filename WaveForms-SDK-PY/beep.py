from WF_SDK import device, scope, wavegen, tools, error   # import instruments
from WF_SDK.device import check_error 
import matplotlib.pyplot as plt   # needed for plotting
import csv                        # needed for saving to CSV
from time import sleep            # needed for delays
import ctypes                     # import the C compatible data types
from sys import platform, path    # this is needed to check the OS type and get the PATH
from os import sep                # OS specific file path separators
import dwfconstants as constants # type: ignore

"""-----------------------------------------------------------------------"""

try:
    # connect to the device
    device_data = device.open()

    """-----------------------------------"""

    # handle devices without analog I/O channels
    if device_data.name != "Digital Discovery":

        # initialize the scope with default settings
        scope.open(device_data)

        scope_ch = 1
        trig = -4
        # set up triggering on scope channel 1
        scope.trigger(device_data, enable=True, source=scope.trigger_source.analog, channel=scope_ch, level=trig)

        sleep(1)    # wait 1 second

        # record data with the scope on channel 1
        buffer = scope.record(device_data, channel=1)

        # limit displayed data size
        length = len(buffer)
        if length > 100000:
            length = 100000
        buffer = buffer[0:length]

        # generate buffer for time moments
        sampling_frequency = scope.data.sampling_frequency
        time = [index * 1e06 / sampling_frequency for index in range(len(buffer))]  # convert time to microseconds

        """-----------------------------------"""
        
        # # Define zoom length
        zoom_length = 100  # Length of zoom in microseconds

        # Calculate the number of data points for 50 microseconds
        num_points = int(zoom_length * sampling_frequency / 1e06)

        # Set zoom start to the middle of the data (or any desired position)
        zoom_start_index = max(0, len(buffer) // 2 - num_points // 2)
        zoom_end_index = min(len(buffer), zoom_start_index + num_points)

        # Extract the zoomed-in data
        zoomed_time = time[zoom_start_index:zoom_end_index]
        zoomed_buffer = buffer[zoom_start_index:zoom_end_index]

        # Plot
        # plt.plot(zoomed_time, zoomed_buffer) 
        # plt.xlabel("Time [µs]")
        # plt.ylabel("Voltage [V]")
        # plt.title(f"{zoom_length} µs time Interval")
        # plt.show()

        """-----------------------------------"""

        filename = fr'C:/Users/thesp/OneDrive/Documents/uv blinker/waveform_data.csv'

            # Open the file in write mode
        with open(filename, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                
                # Write header
                csvwriter.writerow(["Channel", scope_ch])
                csvwriter.writerow(["Trigger Level", trig])
                csvwriter.writerow(["Time [µs]", "Voltage [V]"])
                
                # Write data
                csvwriter.writerows(zip(zoomed_time, zoomed_buffer))

        """-----------------------------------"""

        # reset the scope
        scope.close(device_data)

    """-----------------------------------"""

    # close the connection
    device.close(device_data)

except error as e:
    print(e)
    # close the connection
    device.close(device_data)
