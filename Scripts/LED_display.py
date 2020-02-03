##remember to sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
##before running this on the pi.

import time
import board
import neopixel
import random

pixel_pin = board.D18
num_pixels = 15
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.9, auto_write = False)
d_blue  = (105, 142, 191)
l_blue  = ( 13, 196, 217)
l_purple= (126,  86, 166)
d_purple= (113, 104, 166)
white   = (255, 255, 255)
color_dict = {0: white, 1: d_blue, 2: l_blue, 3: d_purple, 4: l_purple}


def recog_flash(wait, num_flashes, color):
    for x in range(num_flashes): 
        for y in range(0, 255, 1):
            pixels.fill(color_dict[color])
            pixels.show()
            time.sleep(wait/510.0)
        for y in range(255, 0, -1):
            pixels.fill(color_dict[color])
            pixels.show()
            time.sleep(wait/510.0)
    nimbus_refresh()

def thinking_animation(wait, color):
    prev_led = num_pixels + 1
    for x in range(num_pixels * 2):
        rand_led = random.randint(0, num_pixels - 1)
        while(rand_led == prev_led):
            rand_led = random.randint(0, num_pixels - 1)
        rand_color = random.randint(1, 4)
        #pixels[rand_led] = color_dict[rand_color]
        pixels[rand_led] = color_dict[color]
        pixels.show()
        time.sleep(wait / (num_pixels * 2.0))
        nimbus_refresh()

def nimbus_cycle(num_cycles, color):
    for x in range(num_cycles):
        top_led = 14
        for y in range(1, 10, 2):
            pixels[y] = color_dict[color]
            pixels[top_led] = color_dict[color]
            pixels.show()
            top_led -= 1
            time.sleep(.075)
            nimbus_refresh()


def nimbus_refresh():
    pixels.fill((0,0,0))
    pixels.show()


def nimbus_call(color):
    recog_flash(.01, 2, color)
    thinking_animation(2, color)
    nimbus_cycle(6, color)

def main():
    nimbus_call(0)
    nimbus_refresh()

if __name__ == '__main__':
    main()
