from rest_framework import serializers
from api.models import Sounds, Annotations, Lessons, Species, Playlists, Species, GroundTruth, PlaylistTypes
from django.contrib.auth.models import User


class SoundSerializer(serializers.ModelSerializer):

	class Meta:
		model = Sounds
		fields = ('id', 'xc_id', 'species', 'waveform_path',
			'spectrogram_path', 'added_date')


class SpeciesSerializer(serializers.ModelSerializer):

	class Meta:
		model = Species
		fields = ('id', 'eng_name')


class AnnotationSerializer(serializers.ModelSerializer):
	owner = serializers.Field(source='owner.username')
	# user = serializers.HyperlinkedRelatedField(many=False,
	# 						read_only=True, 
	# 						view_name='user-detail',
	# 						format='html')
	# sound = serializers.HyperlinkedRelatedField(many=False,
	# 						read_only=True, 
	# 						view_name='sound-detail',
	# 						format='html')

	class Meta:
		model = Annotations
		fields = ('id', 'user', 'sound', 'wave_onset', 'wave_offset', 
			'spec_onset', 'spec_offset', 'species', 
			'added_date')


class UserSerializer(serializers.ModelSerializer):
	annotations = serializers.PrimaryKeyRelatedField(many=True)
	truth = serializers.PrimaryKeyRelatedField(many=True)
	# annotations = serializers.HyperlinkedRelatedField(many=True,
	# 						read_only=True, 
	# 						view_name='annotation-detail',
	# 						format='html')

	class Meta:
		model = User
		fields = ('id', 'username', 'annotations', 'truth')


class PlaylistSerializer(serializers.ModelSerializer):
	lessons = serializers.PrimaryKeyRelatedField(many=True)

	class Meta:
		model = Playlists
		fields = ('id', 'playlist_name', 'playlist_type',
			'lessons', 'added_date')


class LessonSerializer(serializers.ModelSerializer):
	sounds = serializers.PrimaryKeyRelatedField(many=True)

	class Meta:
		model = Lessons
		fields = ('id', 'playlist', 'sounds', 'added_date')


class SpeciesSerializer(serializers.ModelSerializer):

	class Meta:
		model = Species
		fields = ('id', 'eng_name')


class GroundTruthSerializer(serializers.ModelSerializer):

	class Meta:
		model = GroundTruth
		fields = ('id', 'user', 'sound', 'wave_onset', 'wave_offset', 
			'spec_onset', 'spec_offset', 'species', 
			'added_date')


class PlaylistTypeSerializer(serializers.ModelSerializer):

	class Meta:
		model = PlaylistTypes
		fields = ('id', 'playlist_type')
