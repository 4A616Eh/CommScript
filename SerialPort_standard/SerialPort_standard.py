# -*- coding: iso-8859-1 -*-

##########################################################################
#
# compatibility layer for USPP Library (use standard python serial module)
#
# Copyright (C) 2021 mrx
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
##########################################################################


"""
SerialPort_standard.py - Handle access to serial port by using python serial.

"""

import serial
import builtins


class SerialPortException(builtins.Exception):
    """Exception raise in the SerialPort methods"""
    def __init__(self, args=None):
        self.args=args


class SerialPort:
    """Encapsulate methods for accesing to a serial port."""
    
    def __init__(self, dev, timeout=None, speed=None, mode='232', params=None, flow='None'):
        """Open the serial port named by the string 'dev'

        'dev' can be any of the following strings: '/dev/ttyS0', '/dev/ttyS1',
        ..., '/dev/ttySX' or '/dev/cua0', '/dev/cua1', ..., '/dev/cuaX'.
        
        'timeout' specifies the inter-byte timeout or first byte timeout
        (in miliseconds) for all subsequent reads on SerialPort.
        If we specify None time-outs are not used for reading operations
        (blocking reading).
        If 'timeout' is 0 then reading operations are non-blocking. It
        specifies that the reading operation is to return inmediately
        with the bytes that have already been received, even if
        no bytes have been received.
        
        'speed' is an integer that specifies the input and output baud rate to
        use. Possible values are: 110, 300, 600, 1200, 2400, 4800, 9600,
        19200, 38400, 57600 and 115200.
        If None a default speed of 9600 bps is selected.
        
        'mode' specifies if we are using RS-232 or RS-485. The RS-485 mode
        is half duplex and use the RTS signal to indicate the
        direction of the communication (transmit or recive).
        Default to RS232 mode (at moment, only the RS-232 mode is
        implemented).

        'params' is a list that specifies properties of the serial 
        communication.
        If params=None it uses default values for the number of bits
        per byte (8), the parity (NOPARITY) and the number of stop bits (1)
        else params is the termios package mode array to use for 
        initialization.
        
        'flow' is a choice of 'None' (no flow control), 'Xon/Xoff' (software
        flow control, or 'Hardware' (for RTS/CTS flow control)]

        """
        self.__devName, self.__timeout, self.__speed=dev, timeout, speed
        self.__mode=mode
        self.__params=params
        self.__bytesize=8
        self.__parity='N'
        self.__stopbits=1
        self.__flow=None
        if flow in ['Xon/Xoff', 'Hardware']:
            self.__flow=flow
        if (self.__timeout is not None) and (self.__timeout != 0): 
            self.__timeout = 1.0 / self.__timeout
        if self.__params is not None:
            if len(self.__params) == 3:
                self.__bytesize=int(self.__params[0])
                self.__parity=self.__params[1]
                self.__stopbits=int(self.__params[2])
        try:
            self.__ser=serial.Serial(port=self.__devName,
                baudrate=self.__speed, parity=self.__parity,
                stopbits=self.__stopbits, bytesize=self.__bytesize)
            if self.__flow == 'Xon/Xoff':
                self.__ser.xonxoff = True
            if self.__flow == 'Hardware':
                self.__ser.rtscts = True
        except:
            raise SerialPortException('Unable to open port')

    def __del__(self):
        """Close the serial port
        
        To close the serial port we have to do explicity: del s
        (where s is an instance of SerialPort)
        """
        try:
            self.__ser.close()
        except:
            pass #raise SerialPortException('Unable to close port')    

    def fileno(self):
        """Return the file descriptor for opened device.

        This information can be used for example with the 
        select funcion.
        """
        return self.__ser.fileno()

    def __read1(self):
        """Read 1 byte from the serial port.

        Generate an exception if no byte is read and self.timeout!=0 
        because a timeout has expired.
        """
        byte = self.__ser.read(1)
        if len(byte)==0 and self.__timeout!=0: # Time-out
            raise SerialPortException('Timeout')
        else:
            return byte.decode(encoding='latin_1', errors='ignore')

    def read(self, num=1) -> str:
        """Read num bytes from the serial port.

        Uses the private method __read1 to read num bytes. If an exception
        is generated in any of the calls to __read1 the exception is reraised.
        """
        s=r''
        for i in range(num):
            s = s + SerialPort.__read1(self)
        return s

    def readline(self) -> str:
        """Read a line from the serial port.  Returns input once a '\n'
        character is found.
        Douglas Jones (dfj23@drexel.edu) 09/09/2005.
        """
        s = r''
        while not '\n' in s:
            s = s + SerialPort.__read1(self)
        return s
        
    def write(self, s: bytes):
        """Write the string s to the serial port"""
        self.__ser.write(s)

    def inWaiting(self):
        """Returns the number of bytes waiting to be read"""
        return self.__ser.inWaiting()

    def outWaiting(self):
        """not implemented"""
        return 0

    def getlsr(self):
        """not implemented"""
        return 0

    def get_temt(self):
        """not implemented"""
        return 0

    def flush(self):
        """Discards all bytes from the output or input buffer"""
        self.__ser.flush()
         
    def rts_on(self):
        """ set RTS on """
        self.__ser.setRTS(1)
        return 0

    def rts_off(self):
        """ set RTS off """
        self.__ser.setRTS(0)
        return 0

    def dtr_on(self):
        """ set DTR on """
        self.__ser.setDTR(1)
        return 0

    def dtr_off(self):
        """ set DTR off """
        self.__ser.setDTR(0)
        return 0

    def cts(self):
        """ get CTS """
        return self.__ser.cts

    def cd(self):
        """ get CD """
        return self.__ser.cd

    def dsr(self):
        """ get DSR """
        return self.__ser.dsr

    def ri(self):
        """ get RI """
        return self.__ser.ri
