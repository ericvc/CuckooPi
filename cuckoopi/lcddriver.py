from time import *
import smbus
from time import *


class I2C:

    def __init__(self, addr, port=1):
        self.addr = addr
        self.bus = smbus.SMBus(port)

    ## Write a command
    def write_cmd(self, cmd):

        self.bus.write_byte(self.addr, cmd)
        sleep(0.005)

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


# LCD Address
ADDRESS = 0x27     #Update Address For LCD Here

# commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00

# flags for backlight control
LCD_BACKLIGHT = 0x08
LCD_NOBACKLIGHT = 0x00

enable_bit = 0b00000100
register_bit = 0b00000001


class LCD:


   def __init__(self):

      self.lcd_device = I2C(ADDRESS)
      self.lcd_write(0x03)
      self.lcd_write(0x03)
      self.lcd_write(0x03)
      self.lcd_write(0x02)
      self.lcd_write(LCD_FUNCTIONSET | LCD_2LINE | LCD_5x8DOTS | LCD_4BITMODE)
      self.lcd_write(LCD_DISPLAYCONTROL | LCD_DISPLAYON)
      self.lcd_write(LCD_CLEARDISPLAY)
      self.lcd_write(LCD_ENTRYMODESET | LCD_ENTRYLEFT)
      sleep(0.2)


   # LCD backlight control
   def backlight(self, mode):

      if mode == 0:
         self.lcd_device.write_cmd(LCD_NOBACKLIGHT)

      elif mode == 1:
         self.lcd_device.write_cmd(LCD_BACKLIGHT)


   def lcd_strobe(self, data):
   
      self.lcd_device.write_cmd(data | enable_bit | LCD_BACKLIGHT)
      sleep(.001)
      self.lcd_device.write_cmd(((data & ~enable_bit) | LCD_BACKLIGHT))
      sleep(.0001)


   def lcd_write_four_bits(self, data):
   
      self.lcd_device.write_cmd(data | LCD_BACKLIGHT)
      self.lcd_strobe(data)


   # Write a command to the LCD
   def lcd_write(self, cmd, mode=0):

      self.lcd_write_four_bits(mode | (cmd & 0xF0))
      self.lcd_write_four_bits(mode | ((cmd << 4) & 0xF0))


   # Display a string on the LCD
   def lcd_display_string(self, string, line):

      if line == 1:

         self.lcd_write(0x80)

      if line == 2:

         self.lcd_write(0xC0)

      if line == 3:

         self.lcd_write(0x94)

      if line == 4:

         self.lcd_write(0xD4)

      for char in string:
         
         self.lcd_write(ord(char), register_bit)


   # Clear LCD display
   def lcd_clear(self):

      self.lcd_write(LCD_CLEARDISPLAY)
      self.lcd_write(LCD_RETURNHOME)
