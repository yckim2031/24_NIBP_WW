import numpy as np
import serial
import matplotlib.pyplot as plt
from drawnow import drawnow
import time
# Initialize serial connection
ser = serial.Serial('COM6', 9600)

# Initialize plot
plt.ion()  # Enable interactive mode
fig, ax = plt.subplots()
data = np.array([])
time_data= np.array([])
# Main loop to read and plot data
while True:
    line = ser.readline()
    value = float(line)
    x = time.time()
    data.append(value)
    time_data.append(x)
    ax.clear()
    ax.plot(time_data,data)
        
    ax.set_xlim(x - 10, x)
    ax.set_ylim(min(data)-10, max(data)+10)

    plt.show()
    plt.pause(0.1)
