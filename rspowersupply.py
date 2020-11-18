# -*- coding: utf-8 -*-
"""
Simple class for controlling RS-3000 and 6000-series programmable power supplies

Not tested with 6000-series, and a few features for 6000-series are not implemented.
Please feel free to fork and push these missing features:
* Support for two channels
* STATUS? and SAV, RCL functions

Andreas Svela 2020
"""

import serial
import numpy as np

_port = "COM5"
_connection_settings = {'baudrate': 9600,
                       'parity': serial.PARITY_NONE,
                       'bytesize': serial.EIGHTBITS,
                       'stopbits': serial.STOPBITS_ONE}

def test_connection(port=_port):
    """Simple funtion to test connection to the PSU"""
    with serial.Serial(port=port, **_connection_settings, timeout=1) as dev:
        dev.flush()
        dev.write(b'*IDN?')
        print(dev.readline())


class PowerSupply():
    """Control for RS PRO 3000/6000 Series programmable power supply"""

    def __init__(self, port=_port, connection_settings=_connection_settings,
                 open_with_init=True, timeout=1, verbose=True):
        self.port = port
        self.connection_settings = connection_settings
        self.timeout = timeout
        self.is_open = False
        self.verbose = verbose
        if open_with_init:
            self.open_connection()

    def __enter__(self, **kwargs):
        # The kwargs will be passed on to __init__
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.is_open:
            self.dev.close()

    def open_connection(self, timeout=None):
        # Override class timeout if argument given
        if timeout is not None:
            self.timeout = timeout
        # Failures to connect are usual, so trying a few times
        tries = 3
        while tries > 0:
            try:
                self.dev = serial.Serial(port=self.port, **_connection_settings,
                                         timeout=self.timeout)
            except serial.SerialException:
                if not tries == 1:
                    print("Failed to connect, trying again..")
                else:
                    print("Failed again, will now stop.")
                    raise RuntimeError("Could not connect to {}".format(self.port))
                tries -= 2
            else:
                self.is_open = True
                break
        self.dev.flush()
        self.idn = self.get_idn()
        if self.verbose:
            print(f"Connected to {idn}")

    def get_idn(self):
        self.dev.write(b'*IDN?')
        return self.dev.readline().decode('utf-8')

    def set_output(self, state):
        """Works only for 6000-series!"""
        if 'RS-300' in self.idn:
            raise NotImplementedError("The set_output() function only works with 6000 series")
        command = 'OUT{}'.format(state)
        self.dev.write(bytes(command, 'utf-8'))

    def get_actual_current(self):
        self.dev.write(b'IOUT1?')
        current = float(self.dev.readline())
        # Check if within limits of possible values
        current = current if 0 <= current <= 5 else np.nan
        return current

    def set_current(self, current):
        command = 'ISET1:{}'.format(current)
        self.dev.write(bytes(command, 'utf-8'))

    def get_actual_voltage(self):
        self.dev.write(b'VOUT1?')
        voltage = float(self.dev.readline())
        # Check if within limits of possible values
        voltage = voltage if 0 <= voltage <= 30 else np.nan
        return voltage

    def set_voltage(self, voltage):
        command = 'VSET1:{}'.format(voltage)
        self.dev.write(bytes(command, 'utf-8'))


def test_class():
    with PowerSupply() as psu:
        print("Current voltage", psu.get_actual_voltage())
        print("Set voltage to 2")
        psu.set_voltage(2)
        print("Current voltage", psu.get_actual_voltage())
        print("Set voltage to 0")
        psu.set_voltage(0)


if __name__ == "__main__":
    test_class()
