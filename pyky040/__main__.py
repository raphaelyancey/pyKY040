import sys

args = sys.argv[1:]

dtparam = "dtoverlay=rotary-encoder,pin_a={clk},pin_b={dt},relative_axis=1,steps-per-period=2"

print("NOTE: this tool will NOT write anything, anywhere, unless you allow it explicitely. Chill!")
print("NOTE: pin numbering is BCM (not board).\n")

clk = input('Enter the CLK pin of the encoder: ')
assert isinstance(clk, int)
dt = input('Enter the DT pin of the encoder: ')
assert isinstance(dt, int)

print("\n")
print("To allow pyKY040 to get the encoder events, execute this command:\n")
print("\tsudo echo \"{}\" >> /boot/config.txt\n".format(dtparam.format(clk=clk, dt=dt)))

print("\nDON'T FORGET TO REBOOT for the changes to take effect!\n")
