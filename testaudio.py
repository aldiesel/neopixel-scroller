import time
import math
import numpy as np
import vlc
from pydub import AudioSegment
from pydub.playback import play

#path to file
filePath = ".\\faded.mp3"
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
N = int(fs*dt)
f = range(0,fs/2,fs/N)
tot_e = 1.0
iterMax = min(len(samples),10)
index = np.floor(np.array(bands)*N/fs+1.0)
index = index.astype(int)

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
	tot_e = tot_e + np.mean(energy)
	print sliceEnergy
print 'Name: {0}, Song length: {1}:{2}, Sample Rate: {3} kHz'.format(songName,int(math.floor(minutes)),int(math.floor(sec)),fs/1000.0)
print bands
#print f


#play the file
p = vlc.MediaPlayer(filePath)
p.play()

time.sleep(len(sound)/1000.0)