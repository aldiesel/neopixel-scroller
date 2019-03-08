import time
import math
import random
import numpy as np
import vlc

#from Tkinter import Tk
#from tkinter.filedialog import askopenfilename
import tkFileDialog

from pydub import AudioSegment
from pydub.playback import play

import ftdi1 as ftdi
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.FT232H as FT232H
 
NEOPIXEL_HIGH8 	= 0b11111000
NEOPIXEL_LOW8	= 0b11100000
NEOPIXEL_HIGH3 	= 0b110
NEOPIXEL_LOW3	= 0b100
BYTES_PER_PIXEL	= 3
SPI_BAUD		= 2400000
MAX_INTENSITY	= 40
#BYTES_PER_PIXEL	= 24
#SPI_BAUD		= 6000000 
 
class NeoPixel_FT232H(object):
	def __init__(self, num_pixels, num_rows):
		# Create an FT232H object.
		self.ft232h = FT232H.FT232H()
		# Create a SPI interface for the FT232H object.  Set the SPI bus to 6mhz.
		self.spi    = FT232H.SPI(self.ft232h, max_speed_hz=SPI_BAUD)
		# Create a pixel data buffer and lookup table.
		self.buffer = bytearray(num_pixels*BYTES_PER_PIXEL*3)
		self.lookup = self.build_byte_lookup()
		#print self.lookup
		self.set_brightness(MAX_INTENSITY/2) #set brightness to 25% by default
		self.num_pixels	= num_pixels
		self.rows 		= num_rows
		self.cols 		= num_pixels/num_rows
 
	def build_byte_lookup(self):
		# Create a lookup table to map all byte values to 8 byte values which
		# represent the 6mhz SPI data to generate the NeoPixel signal for the
		# specified byte.
		lookup = {}
		for i in range(256):
			value = bytearray()
			fullint = 0x00
			#for j in range(7, -1, -1):
			#	value.append(NEOPIXEL_LOW8 if (((i >> j) & 1) == 0) else NEOPIXEL_HIGH8)
			for j in range(7, -1, -1):
				signal = NEOPIXEL_LOW3 if (((i >> j) & 1) == 0) else NEOPIXEL_HIGH3
				fullint = fullint | signal
				fullint = fullint << 3
			
			fullint = fullint >> 3
			#print("{0:b}".format(fullint))
			#grab 1 byte at a time and place into the lookup table
			for k in range(2, -1, -1):
				val = (fullint & (0xFF << 8*k)) >> (8*k)
				#print("{0:b}".format(val))
				value.append(val)
				
			lookup[i] = value
		return lookup
	
	def clear_pixels(self):
		nullColor = {'red':0,'green':0,'blue':0}
		for row in range(self.rows):
			for col in range(self.cols):
				pixels.set_pixelRC(row+1,col+1,nullColor)
				
		pixels.show()
 
	def set_pixel_color(self, n, r, g, b):
		# Set the pixel RGB color for the pixel at position n.
		# Assumes GRB NeoPixel color ordering, but it's easy to change below.	
		index = n*BYTES_PER_PIXEL*3
		self.buffer[index  					:index+  BYTES_PER_PIXEL] = self.lookup[int(g*self.bright)]
		self.buffer[index+  BYTES_PER_PIXEL	:index+2*BYTES_PER_PIXEL] = self.lookup[int(r*self.bright)]
		self.buffer[index+2*BYTES_PER_PIXEL	:index+3*BYTES_PER_PIXEL] = self.lookup[int(b*self.bright)]
	
	def set_pixelRC(self, row, col, color):
		# Set the pixel RGB color for the pixel at position n.
		# Assumes GRB NeoPixel color ordering, but it's easy to change below.
		rowOffset = (row if col%2 == 1 else (self.rows+1 - row)) - 1
		colOffset = (col-1)*self.rows
		n = rowOffset + colOffset
		self.set_pixel_color(n,color['red'],color['green'],color['blue'])
	
	def set_brightness(self, brightpcent):
		self.bright = math.pow(min(brightpcent,MAX_INTENSITY)/100.0,2.2)
 
	def show(self):
		# Send the pixel buffer out the SPI data output pin (D1) as a NeoPixel
		# signal.
		self.spi.write(self.buffer)
	
	def setLightColumn(self,maxRow,col,color):
		for row in range(self.rows):
			setColor = color if (row > maxRow) else {'red':0,'green':0,'blue':0}
			self.set_pixelRC(row+1,col,setColor)
 
# Run this code when the script is called at the command line:
if __name__ == '__main__':
	# Define the number of pixels in the NeoPixel strip.
	# Only up to ~340 pixels can be written using the FT232H.
	# Create a NeoPixel_FT232H object.
	pixels = NeoPixel_FT232H(512,8)
	pixels.set_brightness(25)
	delay = 0.02
	# Animate each pixel turning red.
	# Loop through each pixel.
	print 'Total pixels: {0}, Rows: {1}, Columns: {2}'.format(pixels.num_pixels,pixels.rows,pixels.cols)
	pixels.clear_pixels()
	time.sleep(delay)
	maxRows = [0]*pixels.cols
	
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
	
	#Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
	filename = tkFileDialog.askopenfilename() # show an "Open" dialog box and return the path to the selected file
	#root.update()
	filePath = ".\\Lights (Bassnectar Remix).mp3"
	filePath = filename
	fileType = filePath.split('.')[-1]
	songName = filePath.split('\\')[-1].split('.')[0]
	
	#open audio file
	sound = AudioSegment.from_file(filePath, format=fileType)
	maxVolume = sound.max_dBFS
	stereosample = sound.get_array_of_samples()
	#add left and right channels together
	samples = np.add(stereosample[::2],stereosample[1::2])
	
	#figure out how long it is
	minutes = len(sound)/(60000.0)
	sec = 60*(minutes-math.floor(minutes))
	print sound
	
	#setup fft junk
	fs = sound.frame_rate
	dt = 1.0/30.0;
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
	bandIndex = np.floor(np.array(bands)*dt+1.0)
	bandIndex = bandIndex.astype(int)
	
	colors = []
	
	for i in range(11):
		colors.append({'red':0xFF,'green':i*255/10,'blue':0x00})
	for i in range(11):
		colors.append({'red':0xFF-i*255/10,'green':0xFF,'blue':0x00})
	for i in range(11):
		colors.append({'red':0x00,'green':0xFF,'blue':i*255/10})
	for i in range(11):
		colors.append({'red':0x00,'green':0xFF-i*255/10,'blue':0xFF})
	for i in range(11):
		colors.append({'red':i*255/10,'green':0x00,'blue':0xFF})
	for i in range(11):
		colors.append({'red':0xFF,'green':0x00,'blue':0xFF-i*255/10})
		
	#play the file
	p = vlc.MediaPlayer(filePath)
	p.play()
	audioDelay = 0.5
	startTime = nextTime = time.time()
	nextTime = nextTime + audioDelay
	tidx = 0
	dropRate = 2.0
	output = [1]*pixels.cols
	curIntensity = 10
	avgEnergy = 10
	
	while nextTime < startTime + len(sound)/1000.0:
		if time.time() > nextTime:
			dtAdjust = dt if tidx > 1 else 0
			N = int(fs*(dt+dtAdjust))
			f = range(0,fs/2,fs/N)
			bandIndex = np.floor(np.array(bands)*(dt+dtAdjust)+1.0)
			bandIndex = bandIndex.astype(int)
			
			t0 = dt*tidx-dtAdjust
			tf = t0 + dt + dtAdjust
			curVolume = sound[round(1000*t0):round(1000*tf)].max_dBFS
	
			s0 = int(round(fs*t0))
			sf = int(round(fs*(dt+dtAdjust)) + s0)-1
			if sf > len(samples):
				break
			slice = samples[s0:sf]
			sliceFFT = np.fft.rfft(slice)
			sliceFFTA = np.abs(sliceFFT)[0:len(f)-1]
			for ii in range(len(bands)-2):
				energy[ii] = sum(sliceFFTA[bandIndex[ii]:bandIndex[ii+1]])
			sliceEnergy = energy*tidx/tot_e

			tot_e += np.mean(energy)
			for col in range(min(pixels.cols,len(sliceEnergy))):
				maxRows[col] = maxRows[col] + dropRate*dt
				maxRow = (pixels.rows-1)-sliceEnergy[col]
				maxRows[col] = min(maxRow+2,maxRows[col],8)
				maxRows[col] = max(maxRows[col],1)
				maxRowInt = int(maxRow) if int(maxRow) < pixels.rows-1 else min(output[(col-1)%pixels.cols]+1,6)
				maxRowInt = int(maxRow)
				#setColor = colors[(col + tidx) % len(colors)]
				setColor = colors[col]
				pixels.setLightColumn(maxRowInt,col+1,setColor)
				output[col] = maxRowInt
				#pixels.set_pixelRC(int(maxRows[col]),col+1,colors[col])
			#setIntensity = MAX_INTENSITY*(curVolume+6)/(maxVolume+6)
			avgEnergy += (dt/5.0)*(sum(energy) - avgEnergy)
			setIntensity = MAX_INTENSITY*(sum(energy)+sum(energy[0:10]))/(2*avgEnergy)
			alpha = dt/0.5
			curIntensity += alpha*(setIntensity - curIntensity)
			pixels.set_brightness(max(10,curIntensity))
			pixels.show()
			tidx = tidx + 1
			#if tidx >= len(sliceEnergies):
			#	break
			nextTime = startTime + tidx*dt
			#print tidx,time.time(),startTime,nextTime
		time.sleep(0.001)

	print 'Name: {0}, Song length: {1}:{2}, Sample Rate: {3} kHz'.format(songName,int(math.floor(minutes)),int(math.floor(sec)),fs/1000.0)
	#print bands
	#print f