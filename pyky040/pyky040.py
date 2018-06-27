from RPi import GPIO
from time import sleep, time
import logging
from threading import Timer
from os import getenv

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(getenv('DEBUG') or logging.INFO)


class Encoder:

    clk = None
    dt = None
    sw = None

    polling_interval = None  # Polling interval (in ms)
    sw_debounce_time = 100  # Debounce time (for switch only)

    step = 1  # Scale step from min to max
    max_counter = 100  # Scale max
    min_counter = 0  # Scale min
    counter = 0  # Initial scale position
    counter_loop = False  # If True, when at MAX, loop to MIN (-> 0, ..., MAX, MIN, ..., ->)

    clkLastState = None

    inc_callback = None  # Clockwise rotation (increment)
    dec_callback = None  # Anti-clockwise rotation (decrement)
    chg_callback = None  # Rotation (either way)
    sw_callback  = None  # Switch pressed

    def __init__(self, CLK=None, DT=None, SW=None, polling_interval=1):
        if not CLK or not DT:
            raise BaseException("You must specify at least the CLK & DT pins")
        self.clk = CLK
        self.dt = DT
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        if SW is not None:
            self.sw = SW
            GPIO.setup(self.sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Pulled-up because KY-040 switch is shorted to ground when pressed
        self.clkLastState = GPIO.input(self.clk)
        self.polling_interval = polling_interval

    def setup(self, **params):

        # Note: boundaries are inclusive : [min_c, max_c]

        if 'loop' in params and params['loop'] is True:
            self.counter_loop = True
        else:
            self.counter_loop = False

        self.min_counter = params['scale_min']
        self.counter = self.min_counter + 0
        self.max_counter = params['scale_max']

        if 'step' in params:
            self.step = params['step']
        if 'inc_callback' in params:
            self.inc_callback = params['inc_callback']
        if 'dec_callback' in params:
            self.dec_callback = params['dec_callback']
        if 'chg_callback' in params:
            self.chg_callback = params['chg_callback']
        if 'sw_callback' in params:
            self.sw_callback = params['sw_callback']
        if 'sw_debounce_time' in params:
            self.sw_debounce_time = params['sw_debounce_time']

    def watch(self):

        swTriggered = False  # Used to debounce a long switch click (prevent multiple callback calls)

        while True:
            try:

                # Switch part
                if self.sw_callback:
                    if GPIO.input(self.sw) == GPIO.LOW:
                        if not swTriggered:
                            now = time() * 1000
                            if latest_switch_call:
                                if now - latest_switch_call > self.sw_debounce_time:
                                    self.sw_callback()
                            else:  # First call
                                self.sw_callback()
                        swTriggered = True
                        latest_switch_call = now
                    else:
                        swTriggered = False

                # Encoder part
                clkState = GPIO.input(self.clk)
                dtState = GPIO.input(self.dt)

                if clkState != self.clkLastState:

                    if dtState != clkState:

                        if self.counter + self.step <= self.max_counter:
                            # Loop or not, increment if the max isn't reached
                            self.counter += self.step
                        elif (self.counter + self.step >= self.max_counter) and self.counter_loop is True:
                            # If loop, go back to min once max is reached
                            self.counter = self.min_counter

                        if self.inc_callback is not None:
                            self.inc_callback(self.counter)
                        if self.chg_callback is not None:
                            self.chg_callback(self.counter)

                    else:

                        if self.counter - self.step >= self.min_counter:
                            # Same as for max ^
                            self.counter -= self.step
                        elif (self.counter - self.step <= self.min_counter) and self.counter_loop is True:
                            # If loop, go back to max once min is reached
                            self.counter = self.max_counter

                        if self.dec_callback is not None:
                            self.dec_callback(self.counter)
                        if self.chg_callback is not None:
                            self.chg_callback(self.counter)

                self.clkLastState = clkState
                sleep(self.polling_interval / 1000)
            except BaseException as e:
                logger.info("Exiting...")
                logger.info(e)
                GPIO.cleanup()
                break
        return
