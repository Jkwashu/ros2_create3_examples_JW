#!/usr/bin/env python3
# Adapted from: https://tutorials-raspberrypi.com/raspberry-pi-ultrasonic-sensor-hc-sr04/
# GPIO code from: https://hub.libre.computer/t/how-to-control-gpio-via-python-3/601

import gpiod
import time
import sys

DEFAULT_TIMEOUT = 0.1
SPEED_OF_SOUND = 34300

def chip_from_num(num):
    return f'gpiochip{num}'

class Sonar:
    """
    Each Sonar object corresponds to a physical sonar. 

    Attributes:
        chip (int): which GPIO chip is used for the trigger and echo pins
                    Note: Both pins have to be on the same chip
        trig_line (int): Trigger pin line number
        echo_line (int): Echo pin line number
        timeout (float): How much time elapses before we assume no ping 
                         will be heard by the echo.
        
    """

    def __init__(self, chip, trig_line, echo_line, timeout=DEFAULT_TIMEOUT):
        self.chip = chip
        self.trig_line = trig_line
        self.echo_line = echo_line
        self.timeout = timeout

    def read(self):
        """Read this Sonar once, returning a distance in centimeters."""
        with gpiod.Chip(chip_from_num(self.chip)) as chip:
            trig_line = self.get_line(chip, self.trig_line, gpiod.LINE_REQ_DIR_OUT)
            echo_line = self.get_line(chip, self.echo_line, gpiod.LINE_REQ_DIR_IN)

            self.send_ping(trig_line)
            duration = self.listen_for_return(echo_line)

            return duration * SPEED_OF_SOUND / 2

    def get_line(self, chip, line_num, req_dir):
        line = chip.get_line(line_num)
        line.request(consumer=sys.argv[0], type=req_dir)
        return line

    def send_ping(self, trig_line):
        trig_line.set_value(1)
        time.sleep(0.00001)
        trig_line.set_value(0)

    def listen_for_return(self, echo_line):
        init = start = stop = time.time()
        while echo_line.get_value() == 0 and time.time() - init < self.timeout:
            start = time.time()

        while echo_line.get_value() == 1 and time.time() - init < self.timeout:
            stop = time.time()

        return stop - start


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: sonar.py chip trig_line echo_line [-t:timeout] [-p:num_pings]")
    else:
        timeout = DEFAULT_TIMEOUT
        num_pings = None
        for arg in sys.argv:
            if arg.startswith("-t:"):
                timeout = float(arg[3:])
            elif arg.startswith("-p:"):
                num_pings = int(arg[3:])

        sonar = Sonar(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), timeout)
        count = 0
        while num_pings is None or count < num_pings:
            count += 1
            print(sonar.read())
