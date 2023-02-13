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

@date   2023-Feb-10
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
    ## A list to store the x-axis position data
    databx = []
    ## A list to store the y-axis position data
    databy = []

    with serial.Serial('COM4', 115200) as serSend:
        serSend.flush()
        ## Prompting user for KP and setpoint
        params = get_params()

        ## Sending user input to controller
        serSend.write(f"{params[0]}\r\n".encode())
        serSend.write(f"{params[1]}\r\n".encode())

    ## Opening the serial port 'COM4' with a baud rate of 115200 and a timeout of 7 seconds
    with serial.Serial('COM4',115200,timeout = 1) as ser:
        ## Flushing the input buffer of the serial port
        ser.flush()

        ## A loop to continuously read the data from the serial port
        while 1:
            
            ## Reading a line of data from the serial port
            line = ser.readline()

            ## Checking if the line read is equal to 'end'
            if(line == b''):
                print('ended')
                ## Breaking the loop if 'end' is received
                break
            try:
                ## Splitting the received line on ',' to get the x and y position data
                tempx,tempy = (line.strip().split(b','))
                ## Appending the received x and y position data to their respective lists
                databx.append(tempx)
                ## This list handles the y variable data
                databy.append(tempy)
                print(tempx)
                print(tempy)
            except:
                # Printing an error message in case of any error while reading the line

                # Continuing to the next iteration of the loop
                continue

        print('Stop Reading')


    ## Converting the list of X bytes to arrays of float type 
    datax = array.array('f', [0] * len(databx))
    ## Converting the list of X bytes to arrays of float type
    datay = array.array('f', [0] * len(databy))
       
    ## Converting the position data from bytes to float and dividing by 1000 to get the data in seconds and rotations
    for i in range(len(datax)):
        
        ## Finalized X list for plotting
        datax[i] = float(databx[i])/1000
        ## Finalized Y list for plotting
        datay[i] = float(databy[i])/1000


    ## Plotting the received position data
    plt.plot(datax,datay)
    ## Setting the axis limits of the plot
    plt.axis([min(datax),max(datax),min(datay),max(datay) + 0.5])
    ## Adding a label to the x-axis of the plot
    plt.xlabel("Time (S)")
    ## Adding a label to the y-axis of the plot
    plt.ylabel("Position (Rotations)")
    ## Displaying the plot
    plt.show()
