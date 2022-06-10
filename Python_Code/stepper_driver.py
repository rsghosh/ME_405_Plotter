'''@file        stepper_driver.py
   @brief       This file contains a stepper driver class for controlling a TMC4210 and TMC2208.
   @author      Ryan Ghosh
   @copyright   This file is licensed under the CC BY-NC-SA 4.0
                Please visit https://creativecommons.org/licenses/by-nc-sa/4.0/
                for terms and conditions of the license.
   @date        June 10, 2022
'''

import pyb

class Stepper_Driver:
    ''' @brief      A stepper driver class for controlling a TMC4210 and TMC2208.
        @details    Objects of this class can be used to interface with a TMC4210
                    and TMC2208 in order to control a stepper motor.
    '''

    def __init__(self, spi, en, cs, 
                 x_max, v_min, v_max, pulse_div, ramp_div, 
                 a_max, pmul, pdiv):
        ''' @brief              Constructor for Stepper_Driver.
            @details            Sets registers in a TMC4210 with values passed in
                                and enables the step/dir interface.
            @param spi          SPI pin.
            @param en           TMC2208 enable pin.
            @param cs           Chip select pin.
            @param x_max        Max position the stepper can move to, in microsteps.
            @param v_min        V_MIN register value.
            @param v_max        V_MAX register value.
            @param pulse_div    PULSE_DIV register value.
            @param ramp_div     RAMP_DIV register value.
            @param a_max        A_MAX register value.
            @param pmul         PMUL register value.
            @param pdiv         PDIV register value.
        '''

        # set SPI and Pin objects to those passed in
        ## SPI pin
        self.spi = spi      # mode=SPI.CONTROLLER
        
        ## TMC2208 enable pin
        self.en = en        # mode=Pin.OUT_PP
        
        ## Chip select pin
        self.cs = cs        # mode=Pin.OUT_PP

        # set max position
        ## Max position the stepper can move to, in microsteps
        self.x_max = x_max
        
        # enable step/dir interface
        self.enable_step_dir()

        # set initial V_MIN and V_MAX
        self.set_velocity(v_min, v_max)

        # set PULSE_DIV and RAMP_DIV
        self.set_pulse_div(pulse_div)
        self.set_ramp_div(ramp_div)

        # set A_MAX, PMUL, and PDIV
        self.set_acceleration(a_max)
        self.set_pmul(pmul)
        self.set_pdiv(pdiv)

        # set R_M to 00 (ramp_mode)
        self.set_ramp_mode()

    def send_recv(self, send, recv=None):
        ''' @brief          Sends and receives data to and from the TMC4210.
            @details        Sets the chip select pin and uses spi.send_recv
                            to send and receive data to and from the TMC4210
                            via SPI.
            @param send     Datagram to send to the TMC4210.
            @param recv     Datagram in which to store the received datagram.
            @return         Bytes received from the TMC4210.
        '''

        self.cs.low()
        if recv is None:
            recv = self.spi.send_recv(send)
        else:
            self.spi.send_recv(send, recv)
        self.cs.high()

        # # debugging
        # print('\nsend:')
        # self.print_arr(send)
        # send[0] |= 0b00000001
        # self.cs.low()
        # recv_temp = self.spi.send_recv(send)
        # self.cs.high()
        # print('\nrecv:')
        # self.print_arr(recv_temp)

        return recv

    def enable_step_dir(self):
        ''' @brief      Enables the step/dir interface of the TMC4210.
            @details    Sets the en_sd bit to 1 to enable the step/dir interface.
        '''

        # set en_sd bit to 1 and reference switches to normally closed:
        send = bytearray([0b01101000,
                          0b00000000,
                          0b00000000,
                          0b00100001])
        self.send_recv(send)

    def set_ramp_mode(self, mode='ramp_mode'):
        ''' @brief          Sets RAMP_MODE.
            @details        Sets the RAMP_MODE register value to 00 for ramp_mode
                            or 10 for velocity_mode.
            @param mode     Mode to set.
        '''

        send = bytearray([0b00010100,
                          0b00000000,
                          0b00000000,
                          0b00000000])
        if mode == 'velocity_mode':
            send[3] = 0b00000010
        self.send_recv(send)

    def enable(self):
        ''' @brief      Enables the TMC2208.
            @details    Sets the en pin low to enable the TMC2208.
        '''

        # set EN pin on the TMC2208
        self.en.low()

    def disable(self):
        ''' @brief      Disables the TMC2208.
            @details    Sets the en pin high to disable the TMC2208.
        '''

        # set EN pin on the TMC2208
        self.en.high()

    def set_pulse_div(self, pulse_div):
        ''' @brief              Sets PULSE_DIV.
            @details            Sets the PULSE_DIV register value to what is passed in.
            @param pulse_div    PULSE_DIV value to set.
        '''

        # (pulse_div should be a 4-bit unsigned int)

        send = bytearray([0b00011001,
                          0b00000000,
                          0b00000000,
                          0b00000000])
        recv = bytearray(4)
        self.send_recv(send, recv)
        recv[2] &= 0x0F
        recv[2] |= (pulse_div << 4)
        recv[0] = send[0] & 0b11111110
        self.send_recv(recv)

    def set_ramp_div(self, ramp_div):
        ''' @brief              Sets RAMP_DIV.
            @details            Sets the RAMP_DIV register value to what is passed in.
            @param ramp_div     RAMP_DIV value to set.
        '''

        # (ramp_div should be a 4-bit unsigned int)

        send = bytearray([0b00011001,
                          0b00000000,
                          0b00000000,
                          0b00000000])
        recv = bytearray(4)
        self.send_recv(send, recv)
        recv[2] &= 0xF0
        recv[2] |= ramp_div
        recv[0] = send[0] & 0b11111110
        self.send_recv(recv)

    def set_pmul(self, pmul):
        ''' @brief          Sets PMUL.
            @details        Sets the PMUL register value to what is passed in.
            @param pmul     Value of PMUL to set.
        '''

        # (pmul should be a 7-bit unsigned int)

        send = bytearray([0b00010011,
                          0b00000000,
                          0b00000000,
                          0b00000000])
        recv = bytearray(4)
        self.send_recv(send, recv)
        recv[2] &= 0b10000000
        recv[2] |= pmul
        recv[0] = send[0] & 0b11111110
        self.send_recv(recv)

    def set_pdiv(self, pdiv):
        ''' @brief          Sets PDIV.
            @details        Sets the PDIV register value to what is passed in.
            @param pdiv     Value of PDIV to set.
        '''

        # (pdiv should be a 4-bit unsigned int)
        
        send = bytearray([0b00010011,
                          0b00000000,
                          0b00000000,
                          0b00000000])
        recv = bytearray(4)
        self.send_recv(send, recv)
        recv[3] &= 0xF0
        recv[3] |= pdiv
        recv[0] = send[0] & 0b11111110
        self.send_recv(recv)

    def set_velocity(self, v_min, v_max):
        ''' @brief          Sets velocity.
            @details        Sets the V_MIN and V_MAX register values to what is passed in.
            @param v_min    Value of V_MIN to set.
            @param v_max    Value of V_MAX to set.
        '''

        # (v_min and v_max should be 11-bit unsigned ints)
        
        # set V_MIN:
        send = bytearray([0b00000100,
                          0b00000000,
                          0b00000000,
                          0b00000000])
        send[2] = (v_min >> 8) & 0xFF
        send[3] = v_min & 0xFF
        self.send_recv(send)

        # set V_MAX:
        send = bytearray([0b00000110,
                          0b00000000,
                          0b00000000,
                          0b00000000])
        send[2] = (v_max >> 8) & 0xFF
        send[3] = v_max & 0xFF
        self.send_recv(send)

    def set_acceleration(self, acceleration):
        ''' @brief                  Sets acceleration.
            @details                Sets the A_MAX register value to what is passed in.
            @param acceleration     Value of A_MAX to set.
        '''

        # (acceleration should be an 11-bit unsigned int)

        # data to send
        send = bytearray([0b00001100,
                          0b00000000,
                          0b00000000,
                          0b00000000])
        send[2] = (acceleration >> 8) & 0xFF
        send[3] = acceleration & 0xFF

        # send data to set A_MAX
        self.send_recv(send)

    def set_target(self, x_target):
        ''' @brief              Sets X_TARGET.
            @details            Sets the X_TARGET register value to the value
                                that is passed in, in units of microsteps.
            @param x_target     Value of X_TARGET to set.
        '''

        # (x_target should be a 24-bit unsigned int in units of microsteps)

        # limit x_target to x_max
        if x_target > self.x_max:
            x_target = self.x_max

        # set X_TARGET:
        send = bytearray([0b00000000,
                          0b00000000,
                          0b00000000,
                          0b00000000])
        send[1] = (x_target >> 16)
        send[2] = (x_target >> 8) & 0xFF
        send[3] = x_target & 0xFF

        # print("\nsend x_target:")
        # self.print_arr(send)
        
        # print("\nset x_target:")
        self.send_recv(send)

        # # debugging
        # send = bytearray([0b00000001,
        #                   0b00000000,
        #                   0b00000000,
        #                   0b00000000])
        # recv = self.send_recv(send)
        # print("\nrecv x_target:")
        # self.print_arr(recv)

    def target_reached(self, x_target):
        ''' @brief              Indicates whether the target position has been reached.
            @details            Returns True if the motor has reached X_TARGET
                                and False if not.
            @param x_target     Value to check the motor's actual position against.
            @return             True if the target position has been reached, else False.
        '''

        # (x_target should be a 24-bit unsigned int in units of microsteps)
        send = bytearray([0b00000011,
                          0b00000000,
                          0b00000000,
                          0b00000000])
        recv = bytearray(4)
        self.send_recv(send, recv)
        curr_pos = int.from_bytes(recv[1:], 'big', False)
        return curr_pos == x_target

    def set_position(self, x_target):
        ''' @brief              Sets the current position of the stepper.
            @details            Sets the X_TARGET and X_ACTUAL registers to the 
                                position that is passed in, in units of microsteps.
            @param x_target     Value of X_TARGET and X_ACTUAL to set.
        '''

        # (x_target should be a 24-bit unsigned int in units of microsteps)

        # limit x_target to x_max
        if x_target > self.x_max:
            x_target = self.x_max

        # set R_M to 10 (velocity_mode):
        self.set_ramp_mode('velocity_mode')

        # set X_TARGET:
        self.set_target(x_target)

        # set X_ACTUAL:
        send = bytearray([0b00000010,
                          0b00000000,
                          0b00000000,
                          0b00000000])
        send[1] = (x_target >> 16)
        send[2] = (x_target >> 8) & 0xFF
        send[3] = x_target & 0xFF
        self.send_recv(send)

        # set R_M back to 00 (ramp_mode):
        self.set_ramp_mode()

    def home(self):
        ''' @brief      Homes the stepper.
            @details    Moves the stepper towards 0 until the 
                        limit switch is triggered.
        '''

        # set position to x_max
        self.set_position(self.x_max)

        # set REF_CONF to enable left reference switch
        send = bytearray([0b00010101,
                          0b00000000,
                          0b00000000,
                          0b00000000])
        recv = bytearray(4)
        self.send_recv(send, recv)
        recv[2] &= 0xF0
        recv[2] |= 0b00000010
        recv[0] = send[0] & 0b11111110
        self.send_recv(recv)

        # send dummy value to X_LATCHED
        send = bytearray([0b00011100,
                          0b00000000,
                          0b00000000,
                          0b00000000])
        self.send_recv(send)

        # set X_TARGET to 0
        self.set_target(0)
    
    def homing_in_progress(self):
        ''' @brief      Indicates whether homing is in progress.
            @details    Returns True if the stepper is homing and the limit
                        switch has not been triggered yet, else False. If homing
                        is not in progress, the limit switch will be disabled
                        and the stepper's position will be set to 0.
            @return     True if homing is in progress, else False.
        '''

        # read lp bit
        send = bytearray([0b00010101,
                          0b00000000,
                          0b00000000,
                          0b00000000])
        recv = bytearray(4)
        self.send_recv(send, recv)
        lp = recv[1] & 0b00000001
        if not lp:
            # set REF_CONF to disable left reference switch
            send = bytearray([0b00010101,
                              0b00000000,
                              0b00000000,
                              0b00000000])
            recv = bytearray(4)
            self.send_recv(send, recv)
            recv[2] &= 0xF0
            recv[2] |= 0b00000011
            recv[0] = send[0] & 0b11111110
            self.send_recv(recv)

            # set position to 0
            self.set_position(0)
        return bool(lp)

    # for debugging
    def print_arr(self, recv):
        ''' @brief          Print a bytearray.
            @details        Print each byte in the bytearray that has been passed
                            in. This function can be used to check datagrams that
                            are being sent to or received from the TMC4210.
            @param recv     bytearray object to print.
        '''

        for idx,byte in enumerate(recv): print(f"b{3-idx}: {byte:#010b} {byte:#04x}")
