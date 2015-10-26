ecd_lifetime_tester
==========

This program communicates with a variety of electromechanical DPDT relay switches. These DPDT relay switches are contained in a SainSmart relay board and several Keithley 7001s. The relays are connected to a Keithely source-measure-unit (SMU). The basic instruction set for the lifetime tester is the following
1. tell the relay to connect to photodiode A (which measures the light transmission through electrocrhomic device (ECD) 1)
2. once connected, measure the current with the SMU from the photodiode, which tells us the light transmission through ECD 1
3. tell the relay to connect to ECD 1
4. apply a 10 sec voltage ramp and 55 second voltage soak to ECD 1 to transition it from the clear state to the dark state
5. tell the relay to connect to photodiode A
6. measure the current with the SMU from the photodiode, which tells us the light transmission through ECD 1
7. repeat the procedure in serial for each of the 40 devices on the lifetime tester
