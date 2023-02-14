"""!
@file main.py
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
    while 1:
        if ser.any():
            kp = float(ser.readline())
            print(kp)
            setpoint = int(ser.readline())
            print(setpoint)
            break

    # Close the USB-serial port
    #ser.deinit()

    return (kp, setpoint)

def task1_fun(shares):
    """!
    Motor 1
    @param shares A list holding the share and queue used by this task
    """
    # Get references to the share and queue which have been passed to this task
    my_share, my_queue = shares

    while 1:
        try:
            if controller1.run():
                u2.write(f"1 {controller1.motor_data[0]} {controller1.motor_data[1]}\r\n")

        except KeyboardInterrupt:
            motor1.set_duty_cycle(0)
            print("motor shut off")
            break

        yield


def task2_fun(shares):
    """!
    Motor 2
    @param shares A list holding the share and queue used by this task
    """
    # Get references to the share and queue which have been passed to this task
    my_share, my_queue = shares

    while 1:
        try:
            if controller2.run():
                u2.write(f"2 {controller2.motor_data[0]} {controller2.motor_data[1]}\r\n")

        except KeyboardInterrupt:
            motor2.set_duty_cycle(0)
            print("motor shut off")
            break

        yield


# This code creates a share, a queue, and two tasks, then starts the tasks. The
# tasks run until somebody presses ENTER, at which time the scheduler stops and
# printouts show diagnostic information about the tasks, share, and queue.
if __name__ == "__main__":
    ## Create a share to test function and diagnostic printouts
    share0 = task_share.Share('h', thread_protect=False, name="Share 0")

    ## Create a queue to test function and diagnostic printouts
    q0 = task_share.Queue('L', 16, thread_protect=False, overwrite=False,
                          name="Queue 0")

    ## Set up the USB-serial port for streaming data
    u2 = pyb.UART(2, baudrate=115200)
    ## Set up the USB-serial port for listening for inputs
    ser = pyb.UART(2, baudrate=115200, timeout=3)

    ## The creation of the motor 1 object
    motor1 = MotorDriver(Pin.board.PC1, Pin.board.PA0, Pin.board.PA1, 5)

    ## The creation of the motor 2 object
    motor2 = MotorDriver(Pin.board.PA10, Pin.board.PB4, Pin.board.PB5, 3)

    ## The creation of the encoder 1 object
    encoder1 = Encoder(Pin.board.PB6, Pin.board.PB7, 4)

    ## The creation of the encoder 2 object
    encoder2 = Encoder(Pin.board.PC6, Pin.board.PC7, 8)

    ## Inputs from decoder for controller1
    updated_params1 = get_inputs()

    ## Inputs from decoder for controller2
    updated_params2 = get_inputs()

    ## Once motor, encoder and params are collected they are used to create this controller 1 object
    controller1 = Controller(updated_params1[0], updated_params1[1], motor1, encoder1)

    ## Once motor, encoder and params are collected they are used to create this controller 2 object
    controller2 = Controller(updated_params2[0], updated_params2[1], motor2, encoder2)


    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for 
    # debugging and set trace to False when it's not needed
    task1 = cotask.Task(task1_fun, name="Task_1", priority=1, period=50,
                        profile=True, trace=False, shares=(share0, q0))
    task2 = cotask.Task(task2_fun, name="Task_2", priority=1, period=250,
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
