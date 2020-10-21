# Copied and barely edited from: http://fuzzthepiguy.tech/lcd/

from time import sleep, strftime
from subprocess import *
from cuckoopi_py.lcddriver import LCD


lcd = LCD()


lcd.lcd_clear()


try:
    
    while True:

        lcd.lcd_display_string(strftime('TIME: ' '%I:%M %p'), 1)
        lcd.lcd_display_string(strftime('%a, %b %d %Y'), 2)
        sleep(0.1)
        
except:
    
    print("Uh oh. Something happened.")
    
finally:
    
    lcd.lcd_clear()

