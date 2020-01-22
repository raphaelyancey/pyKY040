import sys

args = sys.argv[1:]

param_rotary = "dtoverlay=rotary-encoder,pin_a={clk},pin_b={dt},relative_axis=1,steps-per-period=2"
#param_switch = "dtoverlay=gpio-key,gpio={pin},gpio_pull=up,keycode=40"

print("NOTE: this tool will NOT write anything, anywhere, unless you allow it explicitely. Chill!")
print("NOTE: pin numbering is BCM (not board).\n")

clk = input('Encoder CLK pin: ')
assert isinstance(clk, int)
dt = input('Encoder DT pin: ')
assert isinstance(dt, int)
#sw = input('Encoder SWITCH pin: ')
#assert isinstance(sw, int)

print("\n")
print("To allow pyKY040 to get the encoder events, execute these commands:\n")
print("\tsudo echo \"{}\" >> /boot/config.txt\n".format(param_rotary.format(clk=clk, dt=dt)))
#print("\tsudo echo \"{}\" >> /boot/config.txt\n".format(param_switch.format(pin=sw)))

print("\nDON'T FORGET TO REBOOT for the changes to take effect!\n")
