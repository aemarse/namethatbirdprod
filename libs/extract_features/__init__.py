from essentia import Pool, array
from essentia.standard import *
# from pylab import *


class FeaturesObject():

	# Initialize some empty parameters
	def __init__(self):
		# Set some parameters
		self.frame_size = 1024
		self.hop_size = 512

	def get_onsets(self, in_filename):

		# print in_filename
		# Load the audio (in mono)
		audio = MonoLoader(filename=in_filename)()

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

		# 3) Save the onset locations to a .json file
		# pool_onsets = Pool()
		# pool_onsets.add('onsets.rms', onsets_rms)

		# # By the way, onsets are saved in terms of "seconds"
		# json_filename = in_filename[0:len(in_filename)-3] + 'json'
		# output = YamlOutput(filename=json_filename, format='json')
		# output(pool_onsets)

		# return json_filename


# THIS IS WHERE IT STARTS

# Call C program for writing audio waveform data
# call(["./hello"])

# Get the onsets
# get_onsets()
