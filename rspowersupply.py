# -*- coding: utf-8 -*-
"""
Simple class for controlling RS-3000 and 6000-series programmable power supplies

Not tested with 6000-series, and a few features for 6000-series are not implemented.
Please feel free to fork and push these missing features:
    * Support for two channels
    * STATUS? and SAV, RCL functions

Andreas Svela 2020
"""

import time
import serial
import numpy as np

PORT = "COM18"
_CONNECTION_SETTINGS = {
    "baudrate": 9600,
    "parity": serial.PARITY_NONE,
    "bytesize": serial.EIGHTBITS,
    "stopbits": serial.STOPBITS_ONE,
}


def test_connection(port=PORT):
    """Simple funtion to test connection to the PSU"""
    with serial.Serial(port=port, **_CONNECTION_SETTINGS, timeout=1) as dev:
        dev.flush()
        dev.write("*IDN?".encode())
        print(dev.readline().decode())


class PowerSupply:
    """Control for RS PRO 3000/6000 Series programmable power supply"""

    _is_open = False

    def __init__(
        self,
        port=PORT,
        connection_settings=_CONNECTION_SETTINGS,
        open_on_init=True,
        timeout=1,
        verbose=True,
    ):
        self.port = port
        self.connection_settings = connection_settings
        self.timeout = timeout
        self.verbose = verbose
        if open_on_init:
            self.open_connection()

    def __enter__(self, **kwargs):
        # The kwargs will be passed on to __init__
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._is_open:
            self.dev.close()

    def write(self, command):
        return self.dev.write(command.encode())

    def query(self, command):
        self.dev.write(command.encode())
        ret = self.dev.readline().decode("utf-8").strip()
        # Query again if empty string received
        if ret == "":
            time.sleep(0.2)
            self.dev.write(command.encode())
            ret = self.dev.readline().decode("utf-8").strip()
        return ret

    def open_connection(self, timeout=None):
        # Override class timeout if argument given
        if timeout is not None:
            self.timeout = timeout
        # Failures to connect are usual, so trying a few times
        tries = 3
        while tries > 0:
            try:
                self.dev = serial.Serial(
                    port=self.port, **self.connection_settings, timeout=self.timeout
                )
            except serial.SerialException:
                if not tries == 1:
                    print("Failed to connect, trying again..")
                else:
                    print("Failed again, will now stop.")
                    raise RuntimeError(f"Could not connect to {self.port}")
                tries -= 2
            else:
                self._is_open = True
                break
        self.dev.flush()
        self.idn = self.get_idn()
        if self.verbose:
            print(f"Connected to {self.idn}")

    def get_idn(self):
        return self.query("*IDN?")

    def set_output(self, state):
        """Works only for 6000-series!"""
        if "RS-300" in self.idn:
            raise NotImplementedError(
                "The set_output() function only works with 6000 series"
            )
        self.write(f"OUT{state}")

    def get_actual_current(self):
        current = float(self.query("IOUT1?"))
        # Check if within limits of possible values
        current = current if 0 <= current <= 5 else np.nan
        return current

    def set_current(self, current):
        self.write(f"ISET1:{current}")

    def get_actual_voltage(self):
        voltage = float(self.query("VOUT1?"))
        # Check if within limits of possible values
        voltage = voltage if 0 <= voltage <= 30 else np.nan
        return voltage

    def set_voltage(self, voltage):
        self.write(f"VSET1:{voltage}")


def test():
    with PowerSupply() as psu:
        print(f"Voltage {psu.get_actual_voltage():.2f}")
        print(f"Current {psu.get_actual_current():.2f}")
        print("Set voltage to 2")
        psu.set_voltage(2)
        print(f"Voltage {psu.get_actual_voltage():.2f}")
        print(f"Current {psu.get_actual_current():.2f}")
        print("Set voltage to 1")
        psu.set_voltage(1)


if __name__ == "__main__":
    test()
