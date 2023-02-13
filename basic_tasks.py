"""!
@file basic_tasks.py
    This file contains a demonstration program that runs some tasks, an
    inter-task shared variable, and a queue. The tasks don't really @b do
    anything; the example just shows how these elements are created and run.

@author JR Ridgely
@date   2021-Dec-15 JRR Created from the remains of previous example
@copyright (c) 2015-2021 by JR Ridgely and released under the GNU
    Public License, Version 2. 
"""

import gc
import pyb
import cotask
import task_share
from pyb import Pin as Pin
from encoder_reader import Encoder
from motor_driver import MotorDriver
from controller import Controller

def get_inputs():
    """!
    @brief      This function reads the user's input for the KP and setpoint values from the decoder.
    @details    The function creates a UART object on port 2 with a baudrate of 115200 and a timeout of 5 seconds.
                It then waits for input from the serial communication and reads the KP and setpoint values.
                Finally, it closes the serial communication and returns a tuple of the KP and setpoint values.
    @param      None
    @return     A tuple of the KP and setpoint values.
    """
    # Set up the USB-serial port for listening for inputs
    ser = pyb.UART(2, baudrate=115200, timeout=5)

    while 1:
        if ser.any():
            kp = float(ser.readline())
            setpoint = int(ser.readline())
            break

    # Close the USB-serial port
    #ser.deinit()

    return (kp, setpoint)

def task1_fun(shares):
    """!
    Task which puts things into a share and a queue.
    @param shares A list holding the share and queue used by this task
    """
    # Get references to the share and queue which have been passed to this task
    my_share, my_queue = shares
    
    ## The creation of the motor 1 object
    motor1 = MotorDriver(Pin.board.PC1, Pin.board.PA0, Pin.board.PA1, 5)
    ## The creation of the encoder 1 object
    encoder1 = Encoder(Pin.board.PB6, Pin.board.PB7, 4)
    ## Inputs from decoder
    updated_params = get_inputs()
    ## Once motor, encoder and params are collected they are used to create this controller 1 object
    controller1 = Controller(updated_params[0] , updated_params[1], motor1, encoder1)  

    while True:


        yield 0


def task2_fun(shares):
    """!
    Task which takes things out of a queue and share and displays them.
    @param shares A tuple of a share and queue from which this task gets data
    """
    # Get references to the share and queue which have been passed to this task
    the_share, the_queue = shares

    while True:


        yield 0


# This code creates a share, a queue, and two tasks, then starts the tasks. The
# tasks run until somebody presses ENTER, at which time the scheduler stops and
# printouts show diagnostic information about the tasks, share, and queue.
if __name__ == "__main__":


    # Create a share and a queue to test function and diagnostic printouts
    share0 = task_share.Share('h', thread_protect=False, name="Share 0")
    q0 = task_share.Queue('L', 16, thread_protect=False, overwrite=False,
                          name="Queue 0")

    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for 
    # debugging and set trace to False when it's not needed
    task1 = cotask.Task(task1_fun, name="Task_1", priority=1, period=400,
                        profile=True, trace=False, shares=(share0, q0))
    task2 = cotask.Task(task2_fun, name="Task_2", priority=2, period=1500,
                        profile=True, trace=False, shares=(share0, q0))
    cotask.task_list.append(task1)
    cotask.task_list.append(task2)

    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect()

    # Run the scheduler with the chosen scheduling algorithm. Quit if ^C pressed
    while True:
        try:
            cotask.task_list.pri_sched()
        except KeyboardInterrupt:
            break

    # Print a table of task data and a table of shared information data
    print('\n' + str (cotask.task_list))
    print(task_share.show_all())
    print(task1.get_trace())
    print('')
