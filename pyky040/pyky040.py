from RPi import GPIO
from time import sleep, time
import logging
from threading import Timer
from os import getenv
import warnings

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG if getenv('DEBUG') == '1' else logging.INFO)

try:
    import evdev
except Exception:
    logging.info("The `evdev` package wasn't found, install it if you need to use the `device` mode.")


class Encoder:

    clk = None               # Board pin connected to the encoder CLK pin
    dt = None                # Same for the DT pin
    sw = None                # And for the switch pin
    polling_interval = None  # GPIO polling interval (in ms)
    sw_debounce_time = 250   # Debounce time (for switch only)

    # State
    clk_last_state = None
    sw_triggered = False     # Used to debounce a long switch click (prevent multiple callback calls)
    latest_switch_press = None

    device = None            # Device path (when used instead of GPIO polling)

    step = 1                 # Scale step from min to max
    max_counter = 100        # Scale max
    min_counter = 0          # Scale min
    counter = 0              # Initial scale position
    counter_loop = False     # If True, when at MAX, loop to MIN (-> 0, ..., MAX, MIN, ..., ->)

    inc_callback = None      # Clockwise rotation callback (increment)
    dec_callback = None      # Anti-clockwise rotation callback (decrement)
    chg_callback = None      # Rotation callback (either way)
    sw_callback = None       # Switch pressed callback

    def __init__(self, CLK=None, DT=None, SW=None, polling_interval=1, device=None):

        if device is not None:

            try:
                self.device = evdev.InputDevice(device)
                logger.info("Please note that the encoder switch functionnality isn't handled in `device` mode yet.")
            except OSError:
                raise BaseException("The rotary encoder needs to be installed before use: https://github.com/raphaelyancey/pyky040#install-device")

        else:

            if not CLK or not DT:
                raise BaseException("You must specify at least the CLK & DT pins")

            assert isinstance(CLK, int)
            assert isinstance(DT, int)
            self.clk = CLK
            self.dt = DT
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.setup(self.dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

            if SW is not None:
                assert isinstance(SW, int)
                self.sw = SW
                GPIO.setup(self.sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Pulled-up because KY-040 switch is shorted to ground when pressed

            self.clk_last_state = GPIO.input(self.clk)
            self.polling_interval = polling_interval

    def warnFloatDepreciation(self, i):
        if isinstance(i, float):
            warnings.warn('Float numbers as `scale_min`, `scale_max`, `sw_debounce_time` or `step` will be deprecated in the next major release. Use integers instead.', DeprecationWarning)

    def setup(self, **params):

        # Note: boundaries are inclusive : [min_c, max_c]

        if 'loop' in params and params['loop'] is True:
            self.counter_loop = True
        else:
            self.counter_loop = False

        if 'scale_min' in params:
            assert isinstance(params['scale_min'], int) or isinstance(params['scale_min'], float)
            self.min_counter = params['scale_min']
            self.counter = self.min_counter
            self.warnFloatDepreciation(params['scale_min'])
        if 'scale_max' in params:
            assert isinstance(params['scale_max'], int) or isinstance(params['scale_max'], float)
            self.max_counter = params['scale_max']
            self.warnFloatDepreciation(params['scale_max'])
        if 'step' in params:
            assert isinstance(params['step'], int) or isinstance(params['step'], float)
            self.step = params['step']
            self.warnFloatDepreciation(params['step'])
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
            assert isinstance(params['sw_debounce_time'], int) or isinstance(params['sw_debounce_time'], float)
            self.sw_debounce_time = params['sw_debounce_time']
            self.warnFloatDepreciation(params['sw_debounce_time'])

    def _switch_press(self):
        now = time() * 1000
        if not self.sw_triggered:
            if self.latest_switch_press is not None:
                # Only callback if not in the debounce delta
                if now - self.latest_switch_press > self.sw_debounce_time:
                    self.sw_callback()
            else:  # Or if first press since script started
                self.sw_callback()
        self.sw_triggered = True
        self.latest_switch_press = now

    def _switch_release(self):
        self.sw_triggered = False

    def _clockwise_tick(self):

        if self.counter + self.step <= self.max_counter:
            self.counter += self.step
        elif self.counter + self.step > self.max_counter:
            # If loop, go back to min once max is reached. Else, just set it to max.
            self.counter = self.min_counter if self.counter_loop is True else self.max_counter

        if self.inc_callback is not None:
            self.inc_callback(self.counter)
        if self.chg_callback is not None:
            self.chg_callback(self.counter)

    def _counterclockwise_tick(self):

        if self.counter - self.step >= self.min_counter:
            self.counter -= self.step
        elif self.counter - self.step < self.min_counter:
            # If loop, go back to min once max is reached. Else, just set it to max.
            self.counter = self.max_counter if self.counter_loop is True else self.min_counter

        if self.inc_callback is not None:
            self.dec_callback(self.counter)
        if self.chg_callback is not None:
            self.chg_callback(self.counter)

    def watch(self):

        if self.device is not None:
            for event in self.device.read_loop():
                if event.type == 2:
                    if event.value == 1:
                        self._clockwise_tick()
                    elif event.value == -1:
                        self._counterclockwise_tick()
        else:

            while True:
                try:
                    # Switch part
                    if self.sw_callback:
                        if GPIO.input(self.sw) == GPIO.LOW:
                            self._switch_press()
                        else:
                            self._switch_release()

                    # Encoder part
                    clkState = GPIO.input(self.clk)
                    dtState = GPIO.input(self.dt)

                    if clkState != self.clk_last_state:
                        if dtState != clkState:
                            self._clockwise_tick()
                        else:
                            self._counterclockwise_tick()

                    self.clk_last_state = clkState
                    sleep(self.polling_interval / 1000)

                except BaseException as e:
                    logger.info("Exiting...")
                    logger.info(e)
                    GPIO.cleanup()
                    break
        return
