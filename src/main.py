"""!
@file main.py
    The code is for a control system for two motors. The system first initializes a USB-serial
    communication to receive inputs from the decoder, including the KP and setpoint values.
    Then two motor objects, two encoder objects, and two controller objects are created using the
    motor and encoder objects and the KP and setpoint values. Finally, two tasks are created to
    control each motor using its corresponding controller object, and these tasks run in a cooperative
    multitasking environment provided by the cotask module. The system streams data to the USB-serial
    port and receives inputs from the same port.

@author Ben Elkayam
@author Roey Mevorach
@author Ermias Yemane

@date   2023-Feb-13
"""
"""!
@package gc                 Contains a garbage collector tool.
@package pyb                Contains all micro controller tools we use.
@package cotask             Contains the class to run cooperatively scheduled tasks in amultitasking system.
@package task_share         Contains the class that allows tasks to share data without the risk
                            of data corruption by interrupts.
@package encoder_reader     Contains our encoder driver class and data.
@package motor_driver       Contains our motor driver class that interfaces with the encoder.
@package controller         Contains our controller class which combines the motor and encode classes.
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

    return (kp, setpoint)

def task1_fun(shares):
    """!
    @brief      This function executes task1 by continuously checking if the controller1 has new data and,
                if so, writing it to the u2 share.
    @details    The function takes in a tuple of two shares, one for the `my_share` and one for the `my_queue`.
                It then enters a while loop that runs indefinitely, checking if the `controller1.run()` method
                returns `True` and, if so, writing the first and second elements of `controller1.motor_data`
                to the `u2` share. If a KeyboardInterrupt is raised, the motor is shut off and the loop is broken.
                The function yields control after each iteration of the loop.
    @param      shares A tuple of two shares, one for `my_share` and one for `my_queue`.
    @return     None
    """
    # Get references to the share and queue which have been passed to this task
    # my_share, my_queue = shares

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
    @brief      This function executes task2 by continuously checking if the controller2 has new data and,
                if so, writing it to the u2 share.
    @details    The function takes in a tuple of two shares, one for the `my_share` and one for the `my_queue`.
                It then enters a while loop that runs indefinitely, checking if the `controller2.run()` method
                returns `True` and, if so, writing the first and second elements of `controller2.motor_data`
                to the `u2` share. If a KeyboardInterrupt is raised, the motor is shut off and the loop is broken.
                The function yields control after each iteration of the loop.
    @param      shares A tuple of two shares, one for `my_share` and one for `my_queue`.
    @return     None
    """
    # Get references to the share and queue which have been passed to this task
    # my_share, my_queue = shares

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
