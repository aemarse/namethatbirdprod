from essentia import Pool, array
from essentia.standard import *
import subprocess


class FeaturesObject():

	# Initialize some empty parameters
	def __init__(self):
		# Set some parameters
		self.frame_size = 1024
		self.hop_size = 512
		self.samps_per_px = 256

	def get_onsets(self, in_filename):

		# print in_filename
		# Load the audio (in mono)
		audio, sampleRate, numChan = AudioLoader(filename=in_filename)()
		audio = MonoLoader(filename=in_filename)()

		self.sampleRate = sampleRate

		# 1) Compute onset detection functions
		od = OnsetDetection(method='rms')

		w = Windowing(type='hann')
		fft = FFT()
		c2p = CartesianToPolar()

		pool_features = Pool()

		# print 'Computing onset detection functions'
		for frame in FrameGenerator(audio, frameSize=self.frame_size, hopSize=self.hop_size):
			mag, phase = c2p(fft(w(frame)))
			pool_features.add('features.rms', od(mag, phase))

		# 2) Compute the onset locations
		onsets = Onsets(silenceThreshold=0.14, delay=10)

		# print 'Computing onset locations'
		onsets_rms = onsets(
							array([ pool_features['features.rms'] ]),
							[ 1 ])

		print "Num onsets: " + str(len(onsets_rms))

		return onsets_rms

	def get_waveform(self, in_filename):

		out_filename = in_filename[0:len(in_filename)-3] + 'dat'
		subprocess.call('audiowaveform -i ' + in_filename + ' -o ' + out_filename + ' -z ' + str(self.samps_per_px)
		 + ' -b 8', shell=True)

		return out_filename
