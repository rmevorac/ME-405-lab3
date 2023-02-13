"""!
@file boot.py
This file is the boot script for the motor control system. This script just turns off REPL for UART2.

@author Ben Elkayam
@author Roey Mevorach
@author Ermias Yemane

@date   2023-Feb-10
"""
import pyb
# Turn off the REPL on UART2
pyb.repl_uart(None)