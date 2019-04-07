import time
import math
import random

import ftdi1 as ftdi
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.FT232H as FT232H
 
 
class NeoPixel_FT232H(object):
	def __init__(self, num_pixels, num_rows):
		# Create a libftdi context.
		ctx = None
		ctx = ftdi.new()
		# Define USB vendor and product ID
		vid = 0x0403
		pid = 0x6014
		# Enumerate FTDI devices.
		self.serial = None
		device_list = None
		count, device_list = ftdi.usb_find_all(ctx, vid, pid)
		while device_list is not None:
			# Get USB device strings and add serial to list of devices.
			ret, manufacturer, description, serial = ftdi.usb_get_strings(ctx, device_list.dev, 256, 256, 256)
			print 'return: {0}, manufacturer: {1}, description: {2}, serial: |{3}|'.format(ret,manufacturer,description,serial)
			if 'FTDI' in manufacturer and 'Serial' in description and 'FT' in serial:
				self.serial = serial
			device_list = device_list.next
		# Make sure to clean up list and context when done.
		if device_list is not None:
			ftdi.list_free(device_list)
		if ctx is not None:
			ftdi.free(ctx)	
		
		# Create an FT232H object.
		self.ft232h = FT232H.FT232H(serial=self.serial)
		# Create a SPI interface for the FT232H object.  Set the SPI bus to 6mhz.
		self.spi    = FT232H.SPI(self.ft232h, max_speed_hz=6000000)
		# Create a pixel data buffer and lookup table.
		self.buffer = bytearray(num_pixels*24)
		self.lookup = self.build_byte_lookup()
		self.set_brightness(25) #set brightness to 25% by default
		self.num_pixels = num_pixels
		self.rows = num_rows
		self.cols = num_pixels/num_rows
 
	def build_byte_lookup(self):
		# Create a lookup table to map all byte values to 8 byte values which
		# represent the 6mhz SPI data to generate the NeoPixel signal for the
		# specified byte.
		lookup = {}
		for i in range(256):
			value = bytearray()
			for j in range(7, -1, -1):
				if ((i >> j) & 1) == 0:
					value.append(0b11100000)
				else:
					value.append(0b11111000)
			lookup[i] = value
		return lookup
	
	def clear_pixels(self):
		for row in range(self.rows):
			for col in range(self.cols):
				color = {'red':0,'green':0,'blue':0}
				pixels.set_pixelRC(row+1,col+1,color)
				
		pixels.show()
 
	def set_pixel_color(self, n, r, g, b):
		# Set the pixel RGB color for the pixel at position n.
		# Assumes GRB NeoPixel color ordering, but it's easy to change below.
		index = n*24
		self.buffer[index   :index+8 ] = self.lookup[int(g*self.bright)]
		self.buffer[index+8 :index+16] = self.lookup[int(r*self.bright)]
		self.buffer[index+16:index+24] = self.lookup[int(b*self.bright)]
	
	def set_pixelRC(self, row, col, color):
		# Set the pixel RGB color for the pixel at position n.
		# Assumes GRB NeoPixel color ordering, but it's easy to change below.
		rowOffset = (row if col%2 == 1 else (self.rows+1 - row)) - 1
		colOffset = (col-1)*self.rows
		n = rowOffset + colOffset
		index = n*24
		self.buffer[index   :index+8 ] = self.lookup[int(color['green']*self.bright)]
		self.buffer[index+8 :index+16] = self.lookup[int(color['red']*self.bright)]
		self.buffer[index+16:index+24] = self.lookup[int(color['blue']*self.bright)]
	
	def set_brightness(self, brightpcent):
		self.bright = math.pow(brightpcent/100.0,2.2)
 
	def show(self):
		# Send the pixel buffer out the SPI data output pin (D1) as a NeoPixel
		# signal.
		self.spi.write(self.buffer)
 
 
# Run this code when the script is called at the command line:
if __name__ == '__main__':
	# Define the number of pixels in the NeoPixel strip.
	# Only up to ~340 pixels can be written using the FT232H.
	# Create a NeoPixel_FT232H object.
	pixels = NeoPixel_FT232H(256,8)
	pixels.set_brightness(25)
	delay = 0.05
	# Animate each pixel turning red.
	# Loop through each pixel.
	print 'Total pixels: {0}, Rows: {1}, Columns: {2}'.format(pixels.num_pixels,pixels.rows,pixels.cols)
	pixels.clear_pixels()
	time.sleep(delay)
	
	while(1):
		for row in range(pixels.rows):
			for col in range(pixels.cols):
				color = {'red':255,'green':0,'blue':0}
				pixels.set_pixelRC(row+1,col+1,color)
				
			pixels.show()
			time.sleep(delay)
		
		for row in range(pixels.rows):
			for col in range(pixels.cols):
				color = {'red':0,'green':255,'blue':0}
				pixels.set_pixelRC(row+1,col+1,color)
			pixels.show()
			time.sleep(delay)
				
		for row in range(pixels.rows):
			for col in range(pixels.cols):
				color = {'red':0,'green':0,'blue':255}
				pixels.set_pixelRC(row+1,col+1,color)
			pixels.show()
			time.sleep(delay)
		
		for row in range(pixels.rows):
			for col in range(pixels.cols):
				color = {'red':random.randint(0,255),'green':random.randint(0,255),'blue':random.randint(0,255)}
				pixels.set_pixelRC(row+1,col+1,color)
			pixels.show()
			time.sleep(delay)

	## Animate a pattern of colors marching around the pixels.
	## Create a pattern of colors to display.
	#colors = [ (255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255), 
	#			(0, 0, 255), (255, 0, 255) ]
	#offset = 0
	#print 'Press Ctrl-C to quit.'
	#while True:
	#	# Loop through all the pixels and set their color based on the pattern.
	#	for i in range(pixels.num_pixels):
	#		color = colors[(i+offset)%len(colors)]
	#		pixels.set_pixel_color(i, color[0], color[1], color[2])
	#	pixels.show()
	#	# Increase the offset to make the colors change position.
	#	offset += 1
	#	time.sleep(delay)