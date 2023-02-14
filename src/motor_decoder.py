"""!
@file motor_decoder.py
    This file processes the data from an encoder for readability and motor control. It collects the
    position data in real-time from the serial port and plots the data using the matplotlib library.
    The main function of the script initializes the serial port and then prompts the user for KP and
    setpoint values. These values are then sent to microcontroller and the controller is run with those
    input values. Position and time values are then received in real time from the microcontroller.
    The received data is processed and then plotted, with time on the x-axis and position on the y-axis.
    The final plot is displayed to the user.

@author Ben Elkayam
@author Roey Mevorach
@author Ermias Yemane

@date   2023-Feb-13
"""
"""
@package serial             Contains the tools used for working with serial connections.
@package array              Contains the array class.
@package matplotlib         Contains the tool to plot and chart for both 2D and 3D data representation.
"""
import serial
import array
from matplotlib import pyplot as plt

def get_params():
    '''!
    @brief      Prompts the user to enter KP and setpoint values.
    @details    This function prompts the user for two values, the KP and setpoint,
                which are used to control the motor. It repeatedly prompts the user
                until valid input is entered.
    @param      None
    @return     Tuple of strings, containing the KP and setpoint values.
    '''
    while True:
        try:
            ## Stores the KP value send from the decoder PC
            KP = float(input("Enter a KP: "))
            ## Stores the setpoint value send from the decoder PC
            setpoint = int(input("Enter a setpoint: "))
            return (str(KP), str(setpoint))
        except ValueError:
            print("Please enter a valid input")



if __name__ == "__main__":
    ## A list to store the x-axis time data from controller1
    databx1 = []
    ## A list to store the y-axis position data from controller1
    databy1 = []
    
    ## A list to store the x-axis time data from controller2
    databx2 = []
    ## A list to store the y-axis position data from controller2
    databy2 = []

    with serial.Serial('COM4', 115200) as serSend:
        serSend.flush()
        ## Prompting user for KP and setpoint for controller1
        params1 = get_params()
        
        ## Prompting user for KP and setpoint for controller2
        params2 = get_params()

        # Sending user input to controller1
        serSend.write(f"{params1[0]}\r\n".encode())
        serSend.write(f"{params1[1]}\r\n".encode())
        
        # Sending user input to controller2
        serSend.write(f"{params2[0]}\r\n".encode())
        serSend.write(f"{params2[1]}\r\n".encode())

    ## Opening the serial port 'COM4' with a baud rate of 115200 and a timeout of 7 seconds
    with serial.Serial('COM4',115200,timeout = 3) as ser:
        # Flushing the input buffer of the serial port
        ser.flush()

        # A loop to continuously read the data from the serial port
        while 1:
            
            ## Reading a line of data from the serial port
            line = ser.readline()

            # Checking if the line read is equal to 'end'
            if(line == b''):
                print('ended')
                # Breaking the loop if 'end' is received
                break
            try:
                
                ## Splitting the received line on ' ' to get the controller number, x (time), and y (position) data
                controller_label,tempx,tempy = (line.strip().split(b' '))
                
                # If data is coming from controller1
                if controller_label == b'1':
                    # Appending the received x (time) and y (position) data to their respective lists
                    databx1.append(tempx)
                    databy1.append(tempy)
                # Else data is coming from controller2
                else:
                    # Appending the received x (time) and y (position) data to their respective lists
                    databx2.append(tempx)
                    databy2.append(tempy)
                    
                print(f"{controller_label}: {tempx}, {tempy}")
                
            except:
                # Continuing to the next iteration of the loop
                continue

        print('Stop Reading')


    ## Converting the list of X bytes to arrays of float type for controller1
    datax1 = array.array('f', [0] * len(databx1))
    ## Converting the list of Y bytes to arrays of float type for controller1
    datay1 = array.array('f', [0] * len(databy1))
    
    ## Converting the list of X bytes to arrays of float type for controller2
    datax2 = array.array('f', [0] * len(databx2))
    ## Converting the list of Y bytes to arrays of float type for controller2
    datay2 = array.array('f', [0] * len(databy2))
       
    # Converting the position data from bytes to float and dividing by 1000 to get the data in seconds and rotations
    for i in range(len(datax1)):
        ## Finalized X list for plotting
        datax1[i] = float(databx1[i])/1000
        ## Finalized Y list for plotting
        datay1[i] = float(databy1[i])/1000
        
    # Converting the position data from bytes to float and dividing by 1000 to get the data in seconds and rotations
    for i in range(len(datax2)):
        ## Finalized X list for plotting
        datax2[i] = float(databx2[i])/1000
        ## Finalized Y list for plotting
        datay2[i] = float(databy2[i])/1000
        
    print("Close previous plot to open next plot")
    # Plotting the received position data
    plt.plot(datax1,datay1)
    # Setting the axis limits of the plot
    plt.axis([min(datax1),max(datax1),min(datay1),max(datay1) + 0.5])
    # Adding a label to the x-axis of the plot
    plt.xlabel("Time (S)")
    # Adding a label to the y-axis of the plot
    plt.ylabel("Position (Rotations)")
    # Adding a title to the plot
    plt.title("Controller 1")
    # Displaying the plot
    plt.show()
    
    # Plotting the received position data
    plt.plot(datax2,datay2)
    # Setting the axis limits of the plot
    plt.axis([min(datax2),max(datax2),min(datay2),max(datay2) + 0.5])
    # Adding a label to the x-axis of the plot
    plt.xlabel("Time (S)")
    # Adding a label to the y-axis of the plot
    plt.ylabel("Position (Rotations)")
    # Adding a title to the plot
    plt.title("Controller 2")
    # Displaying the plot
    plt.show()