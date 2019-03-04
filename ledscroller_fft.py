import time
import math
import random
import numpy as np
import vlc

from pydub import AudioSegment
from pydub.playback import play

import ftdi1 as ftdi
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.FT232H as FT232H
 
 
class NeoPixel_FT232H(object):
	def __init__(self, num_pixels, num_rows):
		#devices = FT232H.enumerate_device_serials()
		#for device in devices:
		#	print(device)
		
		## Create temp def
		#vid = 0x0403   # Default FTDI FT232H vendor ID
		#pid = 0x6014   # Default FTDI FT232H product ID
		## Create a libftdi context.
		#ctx = None
		#ctx = ftdi.new()
		## Enumerate FTDI devices.
		#device_list = None
		#count, device_list = ftdi.usb_find_all(ctx, vid, pid)
		#while device_list is not None:
		#	# Get USB device strings and add serial to list of devices.
		#	ret, manufacturer, description, serial = ftdi.usb_get_strings(ctx, device_list.dev, 256, 256, 256)
		#	print 'ret: {0}, manufacturer: {1}, description: {2}, serial: |{3}|'.format(ret,manufacturer,description,serial)
		#	device_list = device_list.next
		## Make sure to clean up list and context when done.
		#if device_list is not None:
		#	ftdi.list_free(device_list)
		#if ctx is not None:
		#	ftdi.free(ctx)	
		
		# Create an FT232H object.
		self.ft232h = FT232H.FT232H()
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
	
	def setLightColumn(self,val,col,color):
		for row in range(self.rows):
			setColor = color if (row < val) else {'red':0,'green':0,'blue':0}
			self.set_pixelRC(row+1,col,setColor)
			#if row > val:
			#	print 'no color'
			#if row == 7 and col == 10:
			#	print val,row+1,col

	
 
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

	#path to file
	filePath = ".\\paris.mp3"
	fileType = filePath.split('.')[-1]
	songName = filePath.split('\\')[-1].split('.')[0]
	
	#open audio file
	sound = AudioSegment.from_file(filePath, format=fileType)
	stereosample = sound.get_array_of_samples()
	left = stereosample[::2]
	right = stereosample[1::2]
	#print len(left),len(right),len(stereosample)
	samples = np.add(left,right)
	#print len(stereosample)/len(samples)
	
	#figure out how long it is
	minutes = len(sound)/(60000.0)
	sec = 60*(minutes-math.floor(minutes))
	print sound
	
	#setup fft junk
	fs = sound.frame_rate
	dt = 1.0/15.0;
	bands = [0,15,30,
			45,60,
			75,90,105,120,
			135,150,165,180,195,210,240,
			255,270,285,300,315,330,360,375,415,480,510,
			525,555,600,630,660,720,750,795,840,885,945,1005,
			1200,1405,1680,1845,2010,
			2400,2810,3330,4020,
			4800,5620,6660,8040]
	while bands[-1] < fs/2 - 500:
		bands.append(bands[-1]+500)
	bands[-1] = fs/2
	energy = np.zeros(len(bands))
	sliceEnergies = []
	N = int(fs*dt)
	f = range(0,fs/2,fs/N)
	tot_e = 1.0
	iterMax = min(len(samples),10)
	iterMax = len(samples)
	index = np.floor(np.array(bands)*N/fs+1.0)
	index = index.astype(int)
	
	colors = [
	{'red':0xFF,'green':0x00,'blue':0x00},{'red':0xFF,'green':0x33,'blue':0x00},{'red':0xFF,'green':0x66,'blue':0x00},{'red':0xFF,'green':0x99,'blue':0x00},
	{'red':0xFF,'green':0xCC,'blue':0x00},{'red':0xFE,'green':0xFF,'blue':0x00},{'red':0xCB,'green':0xFF,'blue':0x00},{'red':0x98,'green':0xFF,'blue':0x00},
	{'red':0x65,'green':0xFF,'blue':0x00},{'red':0x32,'green':0xFF,'blue':0x00},{'red':0x00,'green':0xFF,'blue':0x00},{'red':0x00,'green':0xFF,'blue':0x33},
	{'red':0x00,'green':0xFF,'blue':0x60},{'red':0x00,'green':0xFF,'blue':0x83},{'red':0x00,'green':0xFF,'blue':0xBC},{'red':0x00,'green':0xFF,'blue':0xEA},
	{'red':0x00,'green':0xE5,'blue':0xFF},{'red':0x00,'green':0xB7,'blue':0xFF},{'red':0x00,'green':0x89,'blue':0xFF},{'red':0x00,'green':0x5B,'blue':0xFF},
	{'red':0x00,'green':0x2D,'blue':0xFF},{'red':0x00,'green':0x00,'blue':0xFF},{'red':0x33,'green':0x00,'blue':0xFF},{'red':0x66,'green':0x00,'blue':0xFF},
	{'red':0x98,'green':0x00,'blue':0xFF},{'red':0xCB,'green':0x00,'blue':0xFF},{'red':0xFF,'green':0x00,'blue':0xFF},{'red':0xFF,'green':0x00,'blue':0xCB},
	{'red':0xFF,'green':0x00,'blue':0x98},{'red':0xFF,'green':0x00,'blue':0x66},{'red':0xFF,'green':0x00,'blue':0x33},{'red':0xFF,'green':0x00,'blue':0x00}]
	
	for jj in range(iterMax):
		t0 = int(round(fs*dt*jj))
		tf = int(round(fs*dt) + t0)-1
		if tf > len(samples):
			break
		#print jj,t0,tf
		slice = samples[t0:tf]
		sliceFFT = np.fft.fft(slice)
		sliceFFTA = np.abs(sliceFFT)[0:len(f)-1]
		#if jj == 4:
		#	print index
		for ii in range(len(bands)-2):
			energy[ii] = sum(sliceFFTA[index[ii]:index[ii+1]])
		sliceEnergy = energy*jj/tot_e
		sliceEnergies.append(sliceEnergy)
	
		tot_e = tot_e + np.mean(energy)
		
	#play the file
	p = vlc.MediaPlayer(filePath)
	p.play()
		
	print len(sliceEnergies)
	for e in sliceEnergies:
		for col in range(min(pixels.cols,len(e))):
			pixels.setLightColumn(e[col*2],col+1,colors[col])
		
		#print sliceEnergy
		pixels.show()
		time.sleep(dt*0.87)

	print 'Name: {0}, Song length: {1}:{2}, Sample Rate: {3} kHz'.format(songName,int(math.floor(minutes)),int(math.floor(sec)),fs/1000.0)
	print bands
	#print f