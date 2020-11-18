## Simple class for controlling RS-3000 and 6000-series programmable power supplies

Known issues:
* Sometimes the unit repeatedly returns empty strings when queries are sent

Usage example:
```python
with PowerSupply() as psu:
    print("Actual voltage", psu.get_actual_voltage())
    print("Set voltage to 2V")
    psu.set_voltage(2)
    print("Actual voltage", psu.get_actual_voltage())
    print("Set current to to 1A")
    psu.set_current(1)
    print("Actual current", psu.get_actual_current())
 ```

Not tested with 6000-series, and a few features for 6000-series are not implemented.
Please feel free to fork and push these missing features:
* Support for two channels
* STATUS? and SAV, RCL functions

