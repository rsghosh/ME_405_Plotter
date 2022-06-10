'''@file        pc_plotter.py
   @brief       This file contains a function for plotting the arm position and drawn
                shapes live on a PC to match the physical plotter.
   @author      Ryan Ghosh
   @copyright   This file is licensed under the CC BY-NC-SA 4.0
                Please visit https://creativecommons.org/licenses/by-nc-sa/4.0/
                for terms and conditions of the license.
   @date        June 10, 2022
'''

import serial
import math
import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import imageio

# constants for converting theta to coordinates
W = 270
H = 90
D = 42
RD = 40

# constants for converting microsteps to radians
STEPS_PER_ROTATION  = 200
MICROSTEPS = 8
MS_PER_RADIAN = 1 / (2 * math.pi) * STEPS_PER_ROTATION * MICROSTEPS

# constants for converting microsteps to account for homing angle and motor direction
STEPS_PER_ROTATION  = 200
MOTOR1_HOMING_ANGLE = -int(68.27 / 360 * STEPS_PER_ROTATION * MICROSTEPS * 6)
MOTOR1_POLARITY     = 1
MOTOR2_HOMING_ANGLE = -int((34.7/2 + 60.24 + 0.9) / 40 * STEPS_PER_ROTATION * MICROSTEPS)
MOTOR2_POLARITY     = -1

def revert_motor1_target(microsteps):
    ''' @brief      Converts the motor1 target value for plotting.
        @details    Takes in a target value for motor1 that was sent to
                    the TMC4210 and converts it for plotting, undoing
                    modifications that were made based on the direction
                    of the motor and its angle when the limit switch is triggered.
        @param      Target position in microsteps sent to the TMC4210.
        @return     Target position for motor1 in microsteps for plotting.
    '''

    # revert target position sent to the TMC4210 to 
    # undo homing angle and motor direction modifications
    return microsteps / MOTOR1_POLARITY + MOTOR1_HOMING_ANGLE

def revert_motor2_target(microsteps):
    ''' @brief      Converts the motor2 target value for plotting.
        @details    Takes in a target value for motor2 that was sent to
                    the TMC4210 and converts it for plotting, undoing
                    modifications that were made based on the direction
                    of the motor and its angle when the limit switch is triggered.
        @param      Target position in microsteps sent to the TMC4210.
        @return     Target position for motor2 in microsteps for plotting.
    '''

    # revert target position sent to the TMC4210 to 
    # undo homing angle and motor direction modifications
    return microsteps / MOTOR2_POLARITY + MOTOR2_HOMING_ANGLE

if __name__ == '__main__':

    # variables for plotting
    ## Whether or not the pen is currently down
    pen_down = False

    ## 2D list for the position of the points on the robot
    robot = [[0 for _ in range(3)] for _ in range(2)]   # [x or y][pt idx]

    ## List of lists of (x,y) tuples, with 1 outer list for each shape
    shapes = []

    ## Index of the current shape being drawn
    curr_shape = -1

    # create figure
    plt.ion()
    fig = plt.figure()
    
    # receive data from nucleo
    with serial.Serial('COM4', 115200) as ser:
        ser.flush()
        
        # read data
        i = -1
        started = False
        while(True):

            # read line
            line = ser.readline().decode().strip('\r\n')

            # if end of data
            if line == "END":
                break
            
            # elif new command
            elif line == "PU" or line == "PD":
                started = True
                i += 1

                # pen up
                if line == "PU":
                    pen_down = False
                
                # pen down
                else:

                    # start a new shape if the pen is not down already
                    if not pen_down:
                        curr_shape += 1
                        shapes.append([])
                    pen_down = True
            
            # elif a coordinate pair was sent
            elif started:

                # read theta0 and theta1 from line
                line = line.split(',')
                theta0 = float(line[0])
                theta1 = float(line[1])

                # convert microsteps to radians
                theta0 = revert_motor1_target(theta0) / MS_PER_RADIAN
                theta1 = revert_motor2_target(theta1) / MS_PER_RADIAN

                # robot - point 0 (pivot point)
                robot[0][0] = W
                robot[1][0] = H

                # robot - point 1 (cart position on linear rail)
                alpha = 1/6 * theta0
                arm_radius = -RD * theta1 / (2 * math.pi)
                robot[0][1] = robot[0][0] - arm_radius * math.cos(alpha)
                robot[1][1] = robot[1][0] - arm_radius * math.sin(alpha)

                # robot - point 2 (pen position)
                robot[0][2] = robot[0][1] + D * math.sin(alpha)
                robot[1][2] = robot[1][1] - D * math.cos(alpha)

                # add pen position to current shape if pen down
                if pen_down:
                    shapes[curr_shape].append((robot[0][2], robot[1][2]))

                # clear plot
                plt.clf()

                # plot robot
                plt.plot(robot[0], robot[1])

                # plot all shapes up to and including curr_shape
                for i in range(curr_shape + 1):
                    x_list = []
                    y_list = []
                    for pt in shapes[i]:
                        x_list.append(pt[0])
                        y_list.append(pt[1])
                    plt.plot(x_list, y_list)

                # format plot
                plt.xlabel('x (mm)')
                plt.ylabel('y (mm)')
                axes = plt.gca()
                axes.set_aspect(1)
                plt.xlim(-50, 300)
                plt.ylim(-50, 200)

                # redraw plot
                fig.canvas.draw()
                fig.canvas.flush_events()
