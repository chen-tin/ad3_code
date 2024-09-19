from time import sleep
from WF_SDK import device, scope, wavegen, tools, error   # import instruments
from WF_SDK.device import check_error 
import matplotlib.pyplot as plt   # needed for plotting
from sys import platform, path    # this is needed to check the OS type and get the PATH
from os import sep                # OS specific file path separators
import dwfconstants as constants  # type: ignore
from datetime import datetime    # import datetime for timestamps

trig = -0.1
device_data = device.open()

try:
    # Handle devices without analog I/O channels
    if device_data.name != "Digital Discovery":

        # Initialize the scope with default settings
        scope.open(device_data, amplitude_range=1) 

        for i in range(10):  # 
            start_time = datetime.now()  # Record the start time

            try:
                scope_ch = 1
                # trig = random.choice(trigger_levels)  # Randomly select a trigger level

                # Set up triggering on scope channel 1
                scope.trigger(device_data, enable=True, source=scope.trigger_source.analog, channel=scope_ch, level=trig)

                sleep(0.5)  # Wait 0.5 second or 500 ms

                # Record data with the scope on channel 1
                buffer = scope.record(device_data, channel=1)

                # Limit displayed data size
                length = len(buffer)
                if length > 100000:
                    length = 100000
                buffer = buffer[0:length]

                # Generate buffer for time moments
                sampling_frequency = scope.data.sampling_frequency
                time = [index * 1e06 / sampling_frequency for index in range(len(buffer))]  # Convert time to nanoseconds

                # Define zoom length
                zoom_length = 2  # Length of zoom in nanosecond

                # Calculate the number of data points for the zoom length
                num_points = int(zoom_length * sampling_frequency / 1e06)

                # Set zoom start to the middle of the data (or any desired position)
                zoom_start_index = max(0, len(buffer) // 2 - num_points // 2)
                zoom_end_index = min(len(buffer), zoom_start_index + num_points)

                # Extract the zoomed-in data
                zoomed_time = time[zoom_start_index:zoom_end_index]
                zoomed_buffer = buffer[zoom_start_index:zoom_end_index]

                # Formatting the data to 4 significant figures
                formatted_time = [f"{t:.4g}" for t in zoomed_time]
                formatted_buffer = [f"{v:.4g}" for v in zoomed_buffer]
                
                # Define filename for each iteration
                filename = fr'C:\Users\thesp\OneDrive\Documents\uv blinker\sample_{i+1}_trig_{trig}.txt'

                # Opening the file
                with open(filename, 'w') as txtfile:
                    
                    txtfile.write(f"Channel: {scope_ch}\n")
                    txtfile.write(f"Trigger Level: {trig}\n")
                    txtfile.write(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    txtfile.write(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    txtfile.write("Time [µs] Voltage [V]\n")
                    
                    
                    for t, v in zip(formatted_time, formatted_buffer):
                        txtfile.write(f"{t} {v}\n")
                
                # plt.figure(figsize=(10, 6))
                # plt.plot(zoomed_time, zoomed_buffer)
                # plt.xlabel('Time [µs]')
                # plt.ylabel('Voltage [V]')
                # plt.title('Zoomed Voltage vs Time')
                # plt.grid(True)
                # plt.legend()
                # plt.show()

            except error as e:
                print(e)
                # Continue to the next iteration if an error occurs

finally:
    # Close the scope and device connections
    scope.close(device_data)
    device.close(device_data)
