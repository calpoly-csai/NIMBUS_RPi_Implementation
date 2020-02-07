##remember to sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
##before running this on the pi.

import time
import board
import neopixel
import random

class LED:

    def __init__(self):
        self.pixel_pin = board.D12
        self.num_pixels = 15
        self.pixels = neopixel.NeoPixel(self.pixel_pin, self.num_pixels, brightness=0.9, auto_write = False)
        self.d_blue  = (105, 142, 191)
        self.l_blue  = ( 13, 196, 217)
        self.l_purple= (126,  86, 166)
        self.d_purple= (113, 104, 166)
        self.white   = (255, 255, 255)
        self.color_dict = {0: self.white, 1: self.d_blue, 2: self.l_blue, 3: self.d_purple, 4: self.l_purple}

    def recog_flash(self, wait, num_flashes, color):
        for x in range(num_flashes): 
            for y in range(0, 255, 1):
                self.pixels.fill(self.color_dict[color])
                self.pixels.show()
                time.sleep(wait/510.0)
            for y in range(255, 0, -1):
                self.pixels.fill(self.color_dict[color])
                self.pixels.show()
                time.sleep(wait/510.0)

    def thinking_animation(self, wait, color):
        prev_led = self.num_pixels + 1
        for x in range(self.num_pixels * 2):
            rand_led = random.randint(0, self.num_pixels - 1)
            while(rand_led == prev_led):
                rand_led = random.randint(0, self.num_pixels - 1)
            rand_color = random.randint(1, 4)
            #self.num_pixels[rand_led] = self.color_dict[rand_color]
            self.pixels[rand_led] = self.color_dict[color]
            self.pixels.show()
            time.sleep(wait / (self.num_pixels * 2.0))
            self.nimbus_refresh()
    
    def nimbus_cycle(self, num_cycles, color):
        for x in range(num_cycles):
            top_led = 14
            for y in range(1, 10, 2):
                self.pixels[y] = self.color_dict[color]
                self.pixels[top_led] = self.color_dict[color]
                self.pixels.show()
                top_led -= 1
                time.sleep(.075)
                self.nimbus_refresh()

    def nimbus_refresh(self):
        self.pixels.fill((0,0,0))
        self.pixels.show()

    def nimbus_call(self, color):
        self.recog_flash(.01, 2, color)
        self.thinking_animation(2, color)
        self.nimbus_cycle(6, color)

if __name__ == '__main__':
    led = LED()
    led.nimbus_call(4)
    led.nimbus_refresh()
