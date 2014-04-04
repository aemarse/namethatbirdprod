from api.models import Sounds, Annotations, Lessons, Playlists, Species, GroundTruth, PlaylistTypes
from api.serializers import SoundSerializer, AnnotationSerializer, SpeciesSerializer, UserSerializer, PlaylistSerializer, LessonSerializer, GroundTruthSerializer, PlaylistTypeSerializer, SpeciesSerializer
from api.permissions import IsOwnerOrReadOnly
from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from libs import xeno_canto as xc
from libs import create_lesson as cl
from libs import extract_features as feat
from django.conf import settings
import os
from urllib2 import urlopen


audio_dir = settings.MEDIA_ROOT
SP_PER_LESSON = 4


@api_view(('GET',))
def api_root(request, format=None):
	return Response({
		'users': reverse('user-list', request=request, format=format),
		'sounds': reverse('sound-list', request=request, format=format),
		'annotations': reverse('annotation-list', request=request, format=format),
		'playlists': reverse('playlist-list', request=request, format=format),
		'lessons': reverse('lesson-list', request=request, format=format),
		'truth': reverse('groundtruth-list', request=request, format=format),
		'species': reverse('species-list', request=request, format=format),
	})


class SoundList(generics.ListCreateAPIView):
	"""
	List all sounds, create a sound
	"""
	queryset = Sounds.objects.all()
	serializer_class = SoundSerializer


class SoundDetail(generics.RetrieveUpdateDestroyAPIView):
	"""
	Retrieve, update, or delete a sound instance
	"""
	queryset = Sounds.objects.all()
	serializer_class = SoundSerializer


class AnnotationList(generics.ListCreateAPIView):
	"""
	List all annotations, create an annotation
	"""
	queryset = Annotations.objects.all()
	serializer_class = AnnotationSerializer
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

	# def pre_save(self, obj):
	# 	obj.owner = self.request.user


class AnnotationDetail(generics.RetrieveUpdateDestroyAPIView):
	"""
	Retrieve, update, or delete an annotation instance
	"""
	queryset = Annotations.objects.all()
	serializer_class = AnnotationSerializer
	permission_classes = (permissions.IsAuthenticatedOrReadOnly, 
							IsOwnerOrReadOnly,)

	# def pre_save(self, obj):
	# 	obj.owner = self.request.user


class UserList(generics.ListAPIView):
	queryset = User.objects.all()
	serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
	queryset = User.objects.all()
	serializer_class = UserSerializer


class PlaylistList(generics.ListCreateAPIView):
	"""
	List all playlists, create a playlist
	"""
	# queryset = Playlists.objects.all()
	serializer_class = PlaylistSerializer

	def get_queryset(self):
		"""
		Optionally restricts the returned playlists
		according to a given playlist_type, by filtering
		against a "playlist_type" query parameter in 
		the URL.
		Multiple query params must be separated by: &
		"""
		
		queryset = Playlists.objects.all()
		
		playlist_type = self.request.QUERY_PARAMS.get('playlist_type', None)
		playlist_name = self.request.QUERY_PARAMS.get('playlist_name', None)
		
		print playlist_type
		print playlist_name

		if playlist_type is not None:
			queryset = queryset.filter(playlist_type=playlist_type)

		if playlist_name is not None:
			queryset = queryset.filter(playlist_name=playlist_name)

		return queryset

	def post(self, request, *args, **kwargs):

		# Get the playlist_type and query_params from post body
		playlist_type = request.POST.get('playlist_type')
		playlist_name = request.POST.get('playlist_name')
		csv_filename = request.POST.get('csv_filename')

		# Create a new Playlist object
		# resp = self.create(request, *args, **kwargs)
		# print resp.data['id']		

		# Get the Playlist object we just created so we can modify it further
		# pl_id = resp.data['id']
		# self.curr_playlist = Playlists.objects.get(pk=pl_id)

		# print pl_id

		# First, create or get the PlaylistType object
		try:
			play_type = PlaylistTypes.objects.get(playlist_type=playlist_type)
		except ObjectDoesNotExist:
			play_type = PlaylistTypes(playlist_type=playlist_type)
			play_type.save()

		# Create a new Playlist object
		pl = Playlists(playlist_name=playlist_name, playlist_type=play_type)
		pl.save()
		self.curr_playlist = pl

		# Get species list from CSV file 
		# lesson = cl.Lesson()
		# lesson.filepath = csv_filename
		# sp_list = []
		# sp_list = lesson.csv_to_list()
		sp_list = ['American+Bittern', 'Mallard', 'Snowy+Egret', 'Great+Egret', 'Canada+Goose', 'Gadwall', 'Northern+Shoveler', 'Green+Heron']

		# Get list of id's from species on the list
		pk_list = []
		pk_list = self.make_lessons_from_list(sp_list)

		# Loop through newly created sounds and calculate waveforms/onsets
		# s = Sounds.objects.filter(pk__in=pk_list)

		return Response()

	def make_lessons_from_list(self, species_list):

		# Split sp_list into smaller lists (each representing a lesson)
		lesson_lists = self.split_list(species_list)

		# Loop through the lesson lists
		for sp_list in lesson_lists:

			# Initialize a list for saving the pks of sounds
			snd_pks = []

			# Instantiate a Lessons object
			l = Lessons()
			l.playlist = self.curr_playlist
			l.save()

			# Loop through the returned species
			id_list = []
			for name in sp_list:
				# Instantiate a XenoCantoObject
				xc_obj = xc.XenoCantoObject()

				# Query xeno-canto
				xc_obj.setName(name)
				xc_obj.makeUrl()
				json_obj = xc_obj.get()
				xc_obj.decode(json_obj)
				recs = xc_obj.recs

				# If there are enough recordings
				if len(recs) >= 5:

					# Loop through the recordings	
					num_recs = 0
					for rec in recs:

						# Break if we exceed the desired number of recordings
						if num_recs > 4:
							break

						# Get the id of the current sound
						curr_id = rec['id']
						curr_sp_name = rec['en']
						curr_url = rec['file']

						# Check if it is already in the db
						try:
							s = Sounds.objects.get(xc_id=curr_id)
						except ObjectDoesNotExist:
							# If no, then add to db, id_list
							s = Sounds()
							s.xc_id = curr_id

							# Figure out if there's a species object that matches the species name
							try:
								sp = Species.objects.get(eng_name=curr_sp_name)
								# If there's not one, create it
							except ObjectDoesNotExist:
								sp = Species(eng_name=curr_sp_name)
								sp.save()

							# Add the species to the current sound
							s.species = sp

							# Download the audio file (temp)
							temp_filename = self.download_file(curr_url, curr_id)

							# Instantiate the FeaturesObject
							feat_obj = feat.FeaturesObject()

							# Calculate the waveform data and save the filepath to Sounds object
							waveform_path = feat_obj.get_waveform(temp_filename)
							# s.waveform_path = waveform_path

							# Save the sound
							s.save()
							snd_pks.append(s.pk)

							# Calculate onsets/offsets
							onsets = feat_obj.get_onsets(temp_filename)

							# Create a GroundTruth object for each onset
							for onset in onsets:
								gtruth = GroundTruth(sound=s,
									onset_loc=onset,
									species=s.species)
								gtruth.save()

							# Remove the temp file
							os.remove(temp_filename)

						# Add the id to the list
						id_list.append(curr_id)

						# Increment num_recs
						num_recs += 1

			l.sounds = snd_pks
			l.save()

		return snd_pks


	# Helper function that splits lists into smaller list of "n" elements each
	def split_list(self, sp_list):
		list_splitter = lambda lst, sz: [lst[i:i+sz] for i in range(0, len(lst), sz)]
		out_list = list_splitter(sp_list, SP_PER_LESSON)
		return out_list


	# Helper function for downloading audio files
	def download_file(self, the_url, curr_id):

		conn = urlopen(the_url)

		new_url = conn.geturl()
		conn = urlopen(new_url)

		file_name = audio_dir + curr_id + '.mp3'
		f = open(file_name, 'wb')
		# size = int(conn.info().getheaders("Content-Length")[0])

		block_size = 8192
		while True:
			buf = conn.read(block_size)

			if not buf:
				break

			f.write(buf)

		f.close()

		return file_name


class PlaylistDetail(generics.RetrieveUpdateDestroyAPIView):
	"""
	Retrieve, update, or delete a playlist instance
	"""
	queryset = Playlists.objects.all()
	serializer_class = PlaylistSerializer


class PlaylistTypeList(generics.ListAPIView):
	"""
	List all playlist types
	"""
	queryset = PlaylistTypes.objects.all()
	serializer_class = PlaylistTypeSerializer


class LessonList(generics.ListCreateAPIView):
	"""
	List all lessons, create a lesson
	"""
	# queryset = Lessons.objects.all()
	serializer_class = LessonSerializer

	def get_queryset(self):
		"""
		Optionally restricts the returned playlists
		according to a given playlist_type, by filtering
		against a "playlist_type" query parameter in 
		the URL.
		Multiple query params must be separated by: &
		"""
		
		queryset = Lessons.objects.all()

		the_id = self.request.QUERY_PARAMS.get('id', None)
		playlist = self.request.QUERY_PARAMS.get('playlist', None)
		sounds = self.request.QUERY_PARAMS.get('sounds', None)

		if the_id is not None:
			queryset = queryset.filter(id=the_id)

		if playlist is not None:
			queryset = queryset.filter(playlist=playlist)

		return queryset


class LessonDetail(generics.RetrieveUpdateDestroyAPIView):
	"""
	Retrieve, update, or delete a lesson instance
	"""
	queryset = Lessons.objects.all()
	serializer_class = LessonSerializer


class GroundTruthList(generics.ListCreateAPIView):
	"""
	List all ground truths, create a ground truth
	"""
	queryset = GroundTruth.objects.all()
	serializer_class = GroundTruthSerializer


class GroundTruthDetail(generics.RetrieveUpdateDestroyAPIView):
	"""
	Retrieve, update, or delete a ground truth instance
	"""
	queryset = GroundTruth.objects.all()
	serializer_class = GroundTruthSerializer


class SpeciesList(generics.ListCreateAPIView):
	"""
	List all species, create a species
	"""
	queryset = Species.objects.all()
	serializer_class = SpeciesSerializer


class SpeciesDetail(generics.RetrieveUpdateDestroyAPIView):
	"""
	Retrieve, update, or delete a species instance
	"""
	queryset = Species.objects.all()
	serializer_class = SpeciesSerializer
