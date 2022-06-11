'''@file        tasks.py
   @brief       This file contains the main function for controlling the plotter,
                along with task functions for sending position commands to the
                stepper drivers and to a PC via UART.
   @author      Ryan Ghosh
   @copyright   This file is licensed under the CC BY-NC-SA 4.0
                Please visit https://creativecommons.org/licenses/by-nc-sa/4.0/
                for terms and conditions of the license.
   @date        June 10, 2022
'''

import pyb
import math
from ulab import numpy as np
import array
import time
from stepper_driver import Stepper_Driver
import gc
import cotask
import task_share

# constants for the vector file and converting it
FILENAME = 'drawing.hpgl'
DPI = 1016
MM_PER_IN = 25.4
MAX_MM_DIST = 0.5

# constants for converting coordinates to theta
W = 270
H = 90
D = 42
RD = 40

# TMC4210 and TMC2208 settings
STEPS_PER_ROTATION  = 200
MICROSTEPS          = 8
F_CLK               = 20000000
PULSE_DIV           = 5
RAMP_DIV            = 5

# constants for converting theta to microsteps
MS_PER_RADIAN = 1 / (2 * math.pi) * STEPS_PER_ROTATION * MICROSTEPS

# constants for converting microsteps to account for homing angle and motor direction
STEPS_PER_ROTATION  = 200
MOTOR1_HOMING_ANGLE = -int(68.27 / 360 * STEPS_PER_ROTATION * MICROSTEPS * 6)
MOTOR1_POLARITY     = 1
MOTOR2_HOMING_ANGLE = -int((34.7/2 + 60.24 + 0.9) / 40 * STEPS_PER_ROTATION * MICROSTEPS)
MOTOR2_POLARITY     = -1

# pen positions
PEN_DOWN_DEG = 65.5
PEN_DOWN_MS = int(PEN_DOWN_DEG / 360 * STEPS_PER_ROTATION * MICROSTEPS)
PEN_UP_DEG = 40
PEN_UP_MS = int(PEN_UP_DEG / 360 * STEPS_PER_ROTATION * MICROSTEPS)

# speed settings in rad/s
MOTOR1_SPEED        = 15
MOTOR1_HOMING_SPEED = 3
MOTOR2_SPEED        = 15 
MOTOR2_HOMING_SPEED = 6
MOTOR3_SPEED        = 15
MOTOR3_HOMING_SPEED = 6

# other motor settings
MOTOR1_X_MAX = 20000
MOTOR2_X_MAX = 20000
MOTOR3_X_MAX = 20000
MOTOR1_V_MIN = 10
MOTOR2_V_MIN = 10
MOTOR3_V_MIN = 1
MOTOR1_A_MAX = 80
MOTOR2_A_MAX = 80
MOTOR3_A_MAX = 60

# cmd_type constants
TYPE_PEN_UP     = 1
TYPE_PEN_DOWN   = 2
TYPE_CMDS_DONE  = 3
TYPE_COMMS_DONE = 4

# global variables
## Button flag
share_button_flag = None

## List of stepper commands, in units of microsteps
cmd_list = None

## Stepper_Driver objects for controlling the 3 steppers
drivers = [3]

# button interrupt function
def onButtonPressFCN(IRQ_src):
    ''' @brief          Sets the button flag when the button is pressed.
        @details        An interrupt function triggered when the blue button
                        on the Nucleo is pressed. This function sets the
                        button_flag share to 1 to indicate the button has been pressed.
        @param IRQ_src  Reference to the hardware device that caused the interrupt to occur.
    '''

    global share_button_flag
    share_button_flag.put(1)

## Button interrupt
button_int = pyb.ExtInt(pyb.Pin.cpu.C13, pyb.ExtInt.IRQ_FALLING, 
                        pyb.Pin.PULL_NONE, callback=onButtonPressFCN)

# functions for driving steppers
def get_velocity_setting(rad_per_sec):
    ''' @brief              Converts the velocity value that is passed in.
        @details            Takes in a velocity value in rad/s and converts it to
                            a corresponding value to be used in the V_MIN or V_MAX
                            register of a TMC4210.
        @param rad_per_sec  Velocity value in rad/s.
        @return             Corresponding velocity value to be used in the TMC4210 registers.
    '''

    # see p.31 of TMC4210 datasheet
    R = rad_per_sec / (2 * math.pi) * STEPS_PER_ROTATION * MICROSTEPS   # microstep frequency (Hz)
    return int(R * 2**PULSE_DIV * 2048 * 32 / F_CLK)

def get_acceleration_setting(rad_per_sec2):
    ''' @brief                  Converts the acceleration value that is passed in.
        @details                Takes in an acceleration value in rad/s^2 and converts it
                                to a corresponding value to be used in the A_MAX
                                register of a TMC4210.
        @param rad_per_sec2     Acceleration value in rad/s^2.
        @return                 Corresponding acceleration value to be used in the TMC4210 registers.
    '''

    # see p.31-32 of TMC4210 datasheet
    delta_R = rad_per_sec2 / (2 * math.pi) * STEPS_PER_ROTATION * MICROSTEPS    # microstep frequency (Hz/s)
    return int(delta_R * 2**(PULSE_DIV + RAMP_DIV + 29) / (F_CLK * F_CLK))

def get_pmul_and_pdiv_setting(a_max):
    ''' @brief          Finds values for PMUL and PDIV.
        @details        Finds suitable values for PMUL and PDIV to match the
                        A_MAX value that is passed in, along with the existing
                        RAMP_DIV and PULSE_DIV settings.
        @param a_max    A_MAX value to match with.
        @return         A tuple containing PMUL, PDIV values.
    '''

    # see p.26 of TMC4210 datasheet
    pm =-1
    pd = -1
    p = a_max / (128.0 + 2**(RAMP_DIV - PULSE_DIV))
    p_reduced = p * 0.99

    for pdiv in range(14):
        pmul = int(p_reduced * 8.0 * 2**pdiv) - 128
        if (0 <= pmul) and (pmul <= 127):
            pm = pmul + 128
            pd = pdiv
    
    return pm, pd

def convert_motor1_target(microsteps):
    ''' @brief              Converts a motor1 target value to send to the TMC4210.
        @details            Takes in a target value for motor1 in units of microsteps
                            And converts it to a corresponding value to send to the
                            TMC4210, based on the direction of the motor and its angle
                            when the limit switch is triggered.
        @param microsteps   Target position in microsteps.
        @return             Target position for motor1 that can be sent to the TMC4210.
    '''

    # convert target position in microsteps to a position to send to the TMC4210
    return MOTOR1_POLARITY * (microsteps - MOTOR1_HOMING_ANGLE)

def convert_motor2_target(microsteps):
    ''' @brief              Converts a motor2 target value to send to the TMC4210.
        @details            Takes in a target value for motor2 in units of microsteps
                            And converts it to a corresponding value to send to the
                            TMC4210, based on the direction of the motor and its angle
                            when the limit switch is triggered.
        @param microsteps   Target position in microsteps.
        @return             Target position for motor2 that can be sent to the TMC4210.
    '''

    # convert target position in microsteps to a position to send to the TMC4210
    return MOTOR2_POLARITY * (microsteps - MOTOR2_HOMING_ANGLE)

# motion planning/coordinate conversion functions
def g(x, theta):
    ''' @brief          g(x, theta) function for use in the Newton-Raphson algorithm.
        @details        A function of x and theta that should be driven to 0 to
                        iteratively find the value of theta that satisfies x = f(theta),
                        where x is the desired pen position and theta is the motor positions.
        @param x        tuple of (x_target, y_target).
        @param theta    tuple of (theta0, theta1).
        @return         g(theta) for the theta guess that is passed in.
    '''

    return [x[0] - (W + RD/(2*math.pi)*theta[1]*math.cos(1/6*theta[0]) + D*math.sin(1/6*theta[0])),
            x[1] - (H + RD/(2*math.pi)*theta[1]*math.sin(1/6*theta[0]) - D*math.cos(1/6*theta[0]))]

def dg_dtheta(theta):
    ''' @brief          dg/dtheta(theta) function for use in the Newton-Raphson algorithm.
        @details        A function of theta that is used to iteratively find the
                        value of theta that satisfies x = f(theta),
                        where x is the desired pen position and theta is the motor positions.
        @param theta    tuple of (theta0, theta1).
        @return         dg(theta)/dtheta for the theta guess that is passed in.
    '''

    return np.array([[-1/6*(-RD/(2*math.pi)*theta[1]*math.sin(1/6*theta[0]) + D*math.cos(1/6*theta[0])), -RD/(2*math.pi)*math.cos(1/6*theta[0])],
                     [-1/6*(RD/(2*math.pi)*theta[1]*math.cos(1/6*theta[0]) + D*math.sin(1/6*theta[0])), -RD/(2*math.pi)*math.sin(1/6*theta[0])]])

def NewtonRaphson(fcn, jacobian, guess, thresh):
    ''' @brief              Iteratively solves the roots of y = g(theta).
        @details            Iteratively finds values for theta to drive the passed
                            in fcn to within thresh of 0.
        @param fcn          The function to find the roots of.
        @param jacobian     Jacobian matrix for the system
        @param guess        Initial guess for theta.
        @param thresh       Allowable error when driving fcn to 0.
        @return             Resulting theta roots.
    '''

    theta = guess
    g = fcn(theta)
    while abs(g[0]) > thresh or abs(g[1]) > thresh:
        theta_arr = (np.asarray(theta)).transpose()
        g_arr = (np.asarray(g)).transpose()
        theta_arr = theta_arr - np.dot(np.linalg.inv(jacobian(theta)), g_arr)
        theta = np.ndarray.tolist((theta_arr).transpose())
        g = fcn(theta)
    return theta

def create_cmd_list():
    ''' @brief          Creates a list of motor commands from an hpgl file.
        @details        Converts each command in an hpgl file to a tuple
                        containing the type ("PU" or "PD" for "pen up" or "pen down"),
                        an array of theta0 values to send to the driver1 TMC4210, and
                        an array of theta1 values to send to the driver2 TMC4210.
        @return         A list of command tuples.
    '''

    # read hpgl file
    with open(FILENAME, 'r') as file:
        line = file.readlines()[0]

    # split into commands
    cmd_str_list = line.split(';')

    # remove commands other than PU and PD
    i = 0
    while i < len(cmd_str_list):
        if 'PU' in cmd_str_list[i] or 'PD' in cmd_str_list[i]:
            i += 1
        else:
            cmd_str_list.remove(cmd_str_list[i])

    # split each command into type and coordinates, and convert to mm
    # each element in cmd_list is a tuple with 3 items:
    #   type (str)
    #   x_arr (array.array of floats)
    #   y_arr (array.array of floats)
    cmd_list = []
    for cmd in cmd_str_list:
        type = cmd[0:2]             # str (either PU or PD)
        args = cmd[2:]              # str containing all args
        # if the command has arguments:
        if len(args):
            arg_list = args.split(',')  # str list of arguments

            # spit args into lists of floats
            x_arr = array.array('f')
            y_arr = array.array('f')
            i = 0
            while i < len(arg_list):
                x_arr.append(float(arg_list[i]) / DPI * MM_PER_IN)
                y_arr.append(float(arg_list[i + 1]) / DPI * MM_PER_IN)
                i += 2
            
            # tuple containing type, x coordinates, y coordinates
            cmd_list.append((type, x_arr, y_arr))

    # interpolate and add more points so the max movement distance
    # in any axis is MAX_MM_DIST
    prev_x = None
    prev_y = None
    for cmd_idx in range(len(cmd_list)):
        type = cmd_list[cmd_idx][0]
        x_arr = cmd_list[cmd_idx][1]
        y_arr = cmd_list[cmd_idx][2]
        new_x_arr = array.array('f')
        new_y_arr = array.array('f')
        if prev_x is None:
            prev_x = x_arr[0]
            prev_y = y_arr[0]
            i = 1
        else:
            i = 0
        while i < len(x_arr):
            x_diff = x_arr[i] - prev_x
            y_diff = y_arr[i] - prev_y
            
            # increments - 1 is the number of coordinate pairs that need to be added
            increments = int(math.ceil(max(abs(x_diff), abs(y_diff)) / MAX_MM_DIST))
            for p in range(increments - 1):
                x = prev_x + float(p + 1) / increments * x_diff
                y = prev_y + float(p + 1) / increments * y_diff
                new_x_arr.append(x)
                new_y_arr.append(y)
            new_x_arr.append(x_arr[i])
            new_y_arr.append(y_arr[i])
            prev_x = x_arr[i]
            prev_y = y_arr[i]
            i += 1
        cmd_list[cmd_idx] = (type, new_x_arr, new_y_arr)
    
    # convert to theta angles, then to microsteps, then convert to input for TMC4210
    # theta_guess = [1, -14]
    theta_guess = [2, -10]
    for cmd in cmd_list:
        x_arr = cmd[1]
        y_arr = cmd[2]
        for i in range(len(x_arr)):
            coord_pair = (x_arr[i], y_arr[i])
            theta = NewtonRaphson(lambda theta: g(coord_pair, theta),
                                  dg_dtheta, theta_guess, 1e-4)
            # debugging
            # print("theta %d done" % (i))

            x_arr[i] = convert_motor1_target(int(theta[0] * MS_PER_RADIAN))
            y_arr[i] = convert_motor2_target(int(theta[1] * MS_PER_RADIAN))
            
            theta_guess = theta

    return cmd_list

# for debugging:
def print_cmd_list(cmd_list):
    ''' @brief      Prints out the passed in cmd_list.
        @details    Prints out each command type ("PU" or "PD")
                    with the corrsponding coordinate list below it.
    '''

    for cmd in cmd_list:
        print(cmd[0])
        for i in range(len(cmd[1])):
            print('\t%f, %f' % (cmd[1][i], cmd[2][i]))

# task functions
def task_cmds_fun():
    ''' @brief      Task function for sending commands to the TMC4210s.
        @details    Generator function that waits for a button press to
                    begin, then reads through cmd_list and sets the
                    targets for each stepper driver. The function waits
                    for the current targets to be reached before sending
                    the next ones.
    '''

    global cmd_list
    global drivers

    # wait for button press
    while share_button_flag.get() != 1:
        yield 0

    # execute each command in cmd_list
    for cmd in cmd_list:

        # pen up or pen down
        if cmd[0] == "PU":
            driver3_target = PEN_UP_MS
            drivers[2].set_target(driver3_target)
            share_cmd_type.put(TYPE_PEN_UP)
        else:
            driver3_target = PEN_DOWN_MS
            drivers[2].set_target(driver3_target)
            share_cmd_type.put(TYPE_PEN_DOWN)
        yield 0

        # wait for driver3 (pen motor) to reach position
        while not drivers[2].target_reached(driver3_target):
            yield 0
        
        theta0_arr = cmd[1]
        theta1_arr = cmd[2]
        
        # for each coordinate pair in the command:
        for i in range(len(theta0_arr)):
            driver1_target = int(theta0_arr[i])
            driver2_target = int(theta1_arr[i])
            
            # set target positions
            drivers[0].set_target(driver1_target)
            drivers[1].set_target(driver2_target)
            share_theta0.put(driver1_target)
            share_theta1.put(driver2_target)
            yield 0
            
            # wait for driver1 to reach position
            while not drivers[0].target_reached(driver1_target):
                yield 0

            # wait for driver2 to reach position
            while not drivers[1].target_reached(driver2_target):
                yield 0

    # indicate the end of cmd_list has been reached
    share_cmd_type.put(TYPE_CMDS_DONE)
    yield 0
        
def task_comms_fun():
    ''' @brief      Task function for sending current commands to the PC.
        @details    Generator function that waits for a button press to
                    begin, then sends the current commands to the PC for
                    live plotting in sync with the physical plotter.
    '''

    # create UART object
    uart = pyb.UART(2)
    uart.init(115200, bits=8, parity=0, stop=1)

    # wait for button press
    while share_button_flag.get() != 1:
        yield 0
    
    # write commands to UART2
    last_cmd_type = 0
    cmd_type = share_cmd_type.get()
    while(cmd_type != TYPE_CMDS_DONE):
        
        # get command type
        cmd_type = share_cmd_type.get()

        # write type str ("PU" or "PD") if it has changed
        if cmd_type != last_cmd_type:
            if cmd_type == TYPE_PEN_UP:
                uart.write("PU\r\n")
            elif cmd_type == TYPE_PEN_DOWN:
                uart.write("PD\r\n")
        elif cmd_type > 0:
            # write each coordinate pair ("theta0, theta1")
            uart.write("%d, %d\r\n" % (share_theta0.get(), share_theta1.get()))
        
        last_cmd_type = cmd_type
        yield 0
    
    # write "END"
    uart.write("END\r\n")

    # indicate all tasks have finished
    share_cmd_type.put(TYPE_COMMS_DONE)
    yield 0

if __name__ == '__main__':
    
    # prevent print statements from being sent through uart
    pyb.repl_uart(None)

    # get command list
    ## List of plotter commands
    cmd_list = create_cmd_list()

    ## Clock pin
    clk_pin = pyb.Pin(pyb.Pin.board.PB6, pyb.Pin.OUT_PP)

    # setup timer and timer channel
    ## Timer for TMC4210 clock signal
    tim = pyb.Timer(4, period=3, prescaler=0)

    ## Timer channel for TMC4210 clock signal
    clk = tim.channel(1, pin=clk_pin, mode=pyb.Timer.PWM, pulse_width=2)

    ## SPI
    spi = pyb.SPI(2, pyb.SPI.CONTROLLER, baudrate=1000000, polarity=1, phase=1)

    # setup chip select pins
    ## Chip select pin for driver1
    cs1 = pyb.Pin(pyb.Pin.board.PB8, mode=pyb.Pin.OUT_PP, value=1)
    
    ## Chip select pin for driver2
    cs2 = pyb.Pin(pyb.Pin.board.PB9, mode=pyb.Pin.OUT_PP, value=1)

    ## Chip select pin for driver3
    cs3 = pyb.Pin(pyb.Pin.cpu.C7, mode=pyb.Pin.OUT_PP, value=1)

    # variables for driver1
    ## TMC2208 enable pin for driver1
    en1 = pyb.Pin(pyb.Pin.cpu.C2, mode=pyb.Pin.OUT_PP, value=1)
    
    ## Max position for driver1
    x_max = MOTOR1_X_MAX
    
    ## V_MIN register value for driver1
    v_min = MOTOR1_V_MIN

    ## V_MAX register value for driver1
    v_max = get_velocity_setting(MOTOR1_SPEED)

    ## A_MAX register value for driver1
    a_max = get_acceleration_setting(MOTOR1_A_MAX)
    
    ## PMUL and PDIV register values for driver1
    pmul, pdiv = get_pmul_and_pdiv_setting(a_max)

    # setup driver1
    ## driver1 Stepper_Driver object
    driver1 = Stepper_Driver(spi, en1, cs1,
                                x_max, v_min, v_max, PULSE_DIV, RAMP_DIV, 
                                a_max, pmul, pdiv)

    # variables for driver2
    ## TMC2208 enable pin for driver2
    en2 = pyb.Pin(pyb.Pin.cpu.C3, mode=pyb.Pin.OUT_PP, value=1)
    
    ## Max position for driver2
    x_max = MOTOR2_X_MAX

    ## V_MIN register value for driver2
    v_min = MOTOR2_V_MIN

    ## V_MAX register value for driver2
    v_max = get_velocity_setting(MOTOR2_SPEED)

    ## A_MAX register value for driver2
    a_max = get_acceleration_setting(MOTOR2_A_MAX)

    ## PMUL and PDIV register values for driver2
    pmul, pdiv = get_pmul_and_pdiv_setting(a_max)

    # setup driver2
    ## driver2 Stepper_Driver object
    driver2 = Stepper_Driver(spi, en2, cs2,
                                x_max, v_min, v_max, PULSE_DIV, RAMP_DIV, 
                                a_max, pmul, pdiv)

    # variables for driver3
    ## TMC2208 enable pin for driver3
    en3 = pyb.Pin(pyb.Pin.cpu.C6, mode=pyb.Pin.OUT_PP, value=1)

    ## Max position for driver3
    x_max = MOTOR3_X_MAX

    ## V_MIN register value for driver3
    v_min = MOTOR3_V_MIN

    ## V_MAX register value for driver3
    v_max = get_velocity_setting(MOTOR3_SPEED)

    ## A_MAX register value for driver3
    a_max = get_acceleration_setting(MOTOR3_A_MAX)

    ## PMUL and PDIV register values for driver3
    pmul, pdiv = get_pmul_and_pdiv_setting(a_max)

    # setup driver3
    ## driver3 Stepper_Driver object
    driver3 = Stepper_Driver(spi, en3, cs3,
                                x_max, v_min, v_max, PULSE_DIV, RAMP_DIV, 
                                a_max, pmul, pdiv)

    # put drivers in a list
    ## List of stepper drivers
    drivers = [driver1, driver2, driver3]

    # disable homing and enable motors
    for driver in drivers:
        driver.homing_in_progress()
        driver.enable()

    print("Starting homing.")

    # home motor3
    drivers[2].set_velocity(1, get_velocity_setting(MOTOR3_HOMING_SPEED))
    drivers[2].home()
    while drivers[2].homing_in_progress():
        pass
    drivers[2].set_velocity(MOTOR3_V_MIN, get_velocity_setting(MOTOR3_SPEED))

    print("Motor3 homed.")

    # home motor1
    drivers[0].set_velocity(1, get_velocity_setting(MOTOR1_HOMING_SPEED))
    drivers[0].home()
    while drivers[0].homing_in_progress():
        pass
    drivers[0].set_velocity(MOTOR1_V_MIN, get_velocity_setting(MOTOR1_SPEED))

    print("Motor1 homed.")

    # home motor2
    drivers[1].set_velocity(1, get_velocity_setting(MOTOR2_HOMING_SPEED))
    drivers[1].home()
    while drivers[1].homing_in_progress():
        pass
    drivers[1].set_velocity(MOTOR2_V_MIN, get_velocity_setting(MOTOR2_SPEED))

    print("Motor2 homed.")

    # create shares
    ## Button flag share
    share_button_flag   = task_share.Share ('H', thread_protect = False, 
                                           name = "Share Button Flag")

    ## Command type share
    share_cmd_type      = task_share.Share('H', thread_protect = False, 
                                           name = "Share Command Type")

    ## theta0 share
    share_theta0        = task_share.Share('L', thread_protect = False, 
                                           name = "Share Theta0")
    
    ## theta1 share
    share_theta1        = task_share.Share('L', thread_protect = False,
                                           name = "Share Theta1")
    # create tasks
    ## Task for sending commands to the TMC4210s
    task_cmds   = cotask.Task(task_cmds_fun, name='Task_Commands', 
                              priority=1, period=1, profile=True, trace=False)

    ## Taskf for sending commands to the PC                              
    task_comms  = cotask.Task(task_comms_fun, name='Task_Comms', 
                              priority=2, period=100, profile=True, trace=False)
    cotask.task_list.append(task_cmds)
    cotask.task_list.append(task_comms)

    # run memory garbage collector
    gc.collect()

    print("Waiting for button press.")

    # run scheduler until the entire cmd_list has been finished
    while not share_cmd_type.get() == 3:
        cotask.task_list.pri_sched()

    # disable motors
    for driver in drivers:
        driver.disable()
