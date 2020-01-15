import evdev
import logging
import threading
from os import getenv

logging.basicConfig()
logger = logging.getLogger()

if getenv('DEBUG') == '1':
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)


class Encoder:

    device = None

    step = 1  # Scale step from min to max
    max_counter = 100  # Scale max
    min_counter = 0  # Scale min
    counter = 0  # Initial scale position
    counter_loop = False  # If True, when at MAX, loop to MIN (-> 0, ..., MAX, MIN, ..., ->)

    inc_callback = None  # Clockwise rotation (increment)
    dec_callback = None  # Anti-clockwise rotation (decrement)
    chg_callback = None  # Rotation (either way)
    sw_callback = None  # Switch pressed

    def __init__(self, device='/dev/input/event0', **params):

        try:
            self.device = evdev.InputDevice(device)
        except OSError:
            raise BaseException("The rotary encoder needs to be set up before use: please refer to the README or run `python -m pyky040 setup` for an interactive setup.")

        # Note: boundaries are inclusive : [min_c, max_c]

        if 'loop' in params and params['loop'] is True:
            self.counter_loop = True
        else:
            self.counter_loop = False

        self.counter = self.min_counter + 0

        if 'scale_min' in params:
            assert isinstance(params['scale_min'], int)
            self.min_counter = params['scale_min']
        if 'scale_max' in params:
            assert isinstance(params['scale_max'], int)
            self.max_counter = params['scale_max']
        if 'step' in params:
            assert isinstance(params['step'], int)
            self.step = params['step']
        if 'inc_callback' in params:
            assert callable(params['inc_callback'])
            self.inc_callback = params['inc_callback']
        if 'dec_callback' in params:
            assert callable(params['dec_callback'])
            self.dec_callback = params['dec_callback']
        if 'chg_callback' in params:
            assert callable(params['chg_callback'])
            self.chg_callback = params['chg_callback']
        if 'sw_callback' in params:
            assert callable(params['sw_callback'])
            self.sw_callback = params['sw_callback']
        if 'sw_debounce_time' in params:
            assert isinstance(params['sw_debounce_time'], int)
            self.sw_debounce_time = params['sw_debounce_time']

        threading.Thread(target=self.loop).start()

    def loop(self):
        for event in self.device.read_loop():
            if event.type == 2:
                if event.value == 1:
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
                elif event.value == -1:
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
