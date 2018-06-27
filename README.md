# pyKY040

**High-level Python module for the KY040 rotary encoder and switch** on Raspberry Pi and similar boards that use `RPi.GPIO`

<img src="https://i.imgur.com/vgHjSoY.jpg" width="300" alt="KY-040 rotary encoder and switch">

## Features

- Increment callback
- Decrement callback
- Change callback (increment or decrement)
- Switch press callback

### Options

- Scale mode (internal counter is bound between X and Y, and is given as argument in the callback functions)
- Looped scale mode (from X to Y, then X again)
- Custom scale step

## Installation

`pip install pyky040`

## Usage

### Basic

```python
# Import the module
from pyky040 import pyky040

# Define your callback
def my_callback(scale_position):
    print('Hello world! The scale position is {}'.format(scale_position))

# Init the encoder pins (CLK, DT, SW)
my_encoder = pyky040.Encoder(17, 18, 26)

# Setup the options and callbacks (see documentation)
my_encoder.setup(scale_min=0, scale_max=100, step=1, chg_callback=my_callback)

# Launch the listener
my_encoder.watch()

# Mess with the encoder...
# > Hello world! The scale position is 1
# > Hello world! The scale position is 2
# > Hello world! The scale position is 3
# > Hello world! The scale position is 2
# > Hello world! The scale position is 1
```

### In a thread

As the `watch()` method runs an infinite polling loop, you might want to run it in a thread if you don't want to block the rest of your script, or if you have **multiple encoders** to handle.

```python
# Import the module and threading
from pyky040 import pyky040
import threading

# Define your callback
def my_callback(scale_position):
    print('Hello world! The scale position is {}'.format(scale_position))

# Init the encoder pins
my_encoder = pyky040.Encoder(CLK=17, DT=18, SW=26)

# Setup the options and callbacks (see documentation)
my_encoder.setup(scale_min=0, scale_max=100, step=1, chg_callback=my_callback)

# Create the thread
my_thread = threading.Thread(target=my_encoder.watch)

# Launch the thread
my_thread.start()

# Do other stuff
print('Other stuff...')
while True:
    print('Looped stuff...')
    sleep(1000)
# ... this is also where you can setup other encoders!

# Mess with the encoder...
# > Other stuff...
# > Looped stuff...
# > Hello world! The scale position is 1
# > Hello world! The scale position is 2
# > Hello world! The scale position is 3
# > Looped stuff...
# > Hello world! The scale position is 2

```

**Note:** The interruption of the module when running in threads is not yet handled, you might have to kill it by yourself 🔪

## Documentation

#### `Encoder(CLK=x, DT=y, SW=z)`

Initializes the module with the specified encoder pins.

- Options
  - `polling_interval` Specify the pins polling interval in ms (default 1ms)

#### `Encoder.setup()`

Setup the behavior of the module. All of the following keyword arguments are optional.

- Callbacks
  - `inc_callback (function)` When the encoder is incremented (clockwise). Scale position as first argument.
  - `dec_callback (function)` When the encoder is decremented. Scale position as first argument.
  - `chg_callback (function)` When the encoder is either incremented or decremented. Scale position as first argument.
  - `sw_callback (function)` When the encoder switch is pressed

- Scale mode
  - `scale_min (int/float)` Scale minimum
  - `scale_max (int/float)` Scale maximum
  - `loop (boolean)` Loop mode (defaults to `False`)
  - `step (int/float)` Scale step when incrementing or decrementing

- Options
  - `sw_debounce_time (int/float)` Switch debounce time in ms (allow only one interrupt per X ms, dismiss others)

**Note:** better keep using ints and not floats for more precise results.

#### `Encoder.watch()`

Starts the listener. The pins polling interval is `1ms` by default and can be customized (see `Encoder()`).

## CHANGELOG

**0.1.2**

  - Changed `__init_` args to kwargs for better readability and ease of use `Encoder(CLK=x, DT=y, SW=z)`
  - Added customizable debounce time (in ms) for the switch `setup(..., sw_debounce_time=300)`
  - Added customizable polling interval (in ms) `Encoder(..., polling_interval=1)`
