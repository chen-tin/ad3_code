import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

print('it works')

# File paths for the two TXT files
data1 = 'C:/newpeak height datas/peakheight.txt'
data2 = 'C:/newpeak height datas/peakheight_2.txt'

print('it started')

# Load data from each file
peak_height1 = np.loadtxt(data1, delimiter=',')
peak_height2 = np.loadtxt(data2, delimiter=',')

# Combine the data from both files
combined_peak_height = np.concatenate((peak_height1, peak_height2))

# Set up the plot style
sns.set(style="darkgrid")

# Create the figure and axis objects
fig, ax = plt.subplots(figsize=(12, 8))

# Plot the combined histogram with enhanced style
n, bins, patches = ax.hist(combined_peak_height, bins=250, color='royalblue', edgecolor='black', alpha=0.75)

# Add a color gradient to the histogram bars
for patch, bin_left, bin_right in zip(patches, bins[:-1], bins[1:]):
    plt.setp(patch, 'facecolor', plt.cm.viridis((bin_left + bin_right) / max(bins)))

# Set the labels and title
ax.set_xlabel('Peak Voltage', fontsize=15, fontweight='bold')
ax.set_ylabel('Counts', fontsize=15, fontweight='bold')
ax.set_yscale('symlog')  # Set the y-axis to a symmetrical logarithmic scale
ax.set_title('Radiation Background Spectrum', fontsize=18, fontweight='bold')

# Add a grid
ax.grid(True, which='both', linestyle='--', linewidth=0.7, alpha=0.7)

# Add minor ticks for better readability
ax.minorticks_on()
ax.tick_params(axis='both', which='major', labelsize=12)
ax.tick_params(axis='both', which='minor', labelsize=10)

# Display the plot
plt.tight_layout()
plt.show()

# Confirmation message
print('Script execution finished')
