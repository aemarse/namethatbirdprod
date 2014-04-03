import libs.xeno_canto as xeno_canto
import csv

#--------------------------------------------------
# GLOBAL VARS
#--------------------------------------------------

RECS_PER_SPECIES = 5
SPECIES_PER_LESSON = 4

#--------------------------------------------------
# LESSON CLASS
#--------------------------------------------------

class Lesson:

	#---------
	# PURPOSE
	#---------
	"""
	Take in various parameters (species names, location), query
	the xeno-canto API, and organize the recordings into a 
	"lesson"
	"""
	
	#---------
	# METHODS
	#---------

	# Initializes class fields
	def __init__(self):
		self.the_list = []
		self.filepath = ""
		self.lesson = []


	# Creates lesson based on list of species in a csv file
	def from_csv(self, filepath):
		self.filepath = filepath
		self.the_list = self.csv_to_list()
		self.lesson = self.from_list()
		return self.lesson


	# Creates lesson based on list of species
	def from_species_list(self, species):
		self.the_list.append(species)
		self.lesson = self.from_list()
		return self.lesson


	# Creates lesson based on a location
	def from_loc(self, loc):
		self.the_list.append(loc)
		self.lesson = self.from_list()
		return self.lesson


	# Class helper method to create a lesson from a list
	def from_list(self):

		id_list = []

		# Loop through species list and perform xeno_canto queries
		for name in self.the_list:

			# Instantiate an empty XenoCantoObject
			xc = xeno_canto.XenoCantoObject()

			# Query xeno-canto
			xc.setName(name) # Set the species name for the query
			xc.makeUrl() # Make the query url
			json_obj = xc.get() # Make the query and ret JSON object
			xc.decode(json_obj) # Decode the JSON obj
			recs = xc.recs # Get the recordings from JSON obj

			# If there are enough recordings...
			if len(recs) >= RECS_PER_SPECIES:

				num_recs = 0

				# loop through the recordings
				for rec in recs:

					# Break if we exceed the number of desired recs
					if num_recs >= RECS_PER_SPECIES:
						break

					id_list.append(rec['id'])

					num_recs += 1

		return id_list


	# Takes in csv file, spits out a list of values
	def csv_to_list(self):
		sp_list = []
		print "Reading in the file: " + self.filepath
		# Read through the csv file and save its contents to list
		with open(self.filepath, 'rb') as csvfile:
			reader = csv.reader(csvfile, delimiter=',', quotechar="\"")
			for row in reader:
				sp = space_to_plus(row)# Convert ' ' to '+'
				sp_list.append(sp)
				print sp

		return sp_list


#--------------------------------------------------
# HELPER FUNCTIONS
#--------------------------------------------------

# Replaces ' ' with '+'
def space_to_plus(sp_l):
	sp = ''.join(sp_l)
	sp = str.replace(sp, ' ', '+',).lower()
	return sp