import smbus
from time import *


class I2C:

    def __init__(self, addr, port=1):
        self.addr = addr
        self.bus = smbus.SMBus(port)

    ## Write a command
    def write_cmd(self, cmd):

        self.bus.write_byte(self.addr, cmd)
        sleep(0.0001)

    ## Write command and argument
    def write_cmd_arg(self, cmd, data):

        self.bus.write_byte_data(self.addr, cmd, data)
        sleep(0.0001)

    ## Write block of data
    def write_block_data(self, cmd, data):

        self.bus.write_block_data(self.addr, cmd, data)
        sleep(0.0001)

    ## Read a single byte
    def read(self):

        return self.bus.read_byte(self.addr)

    ## Read bytes
    def read_data(self, cmd):

        return self.bus.read_byte_data(self.addr, cmd)

    ## Read a block of data
    def read_block_data(self, cmd):

        return self.bus.read_block_data(self.addr, cmd)